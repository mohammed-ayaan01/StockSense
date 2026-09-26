"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "MANAGER", "STAFF", name="userrole"), nullable=False, server_default="STAFF"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # otp_tokens
    op.create_table(
        "otp_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hashed_otp", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # units_of_measure
    op.create_table(
        "units_of_measure",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("abbreviation", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # products
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False, unique=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("uom_id", sa.Integer(), sa.ForeignKey("units_of_measure.id"), nullable=False),
        sa.Column("unit_cost", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reorder_threshold", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # warehouses
    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # locations
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("warehouse_id", "code", name="uq_location_warehouse_code"),
    )

    # inventory_stock
    op.create_table(
        "inventory_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("reserved", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("product_id", "location_id", name="uq_stock_product_location"),
        sa.CheckConstraint("quantity >= 0", name="ck_stock_quantity_nonneg"),
        sa.CheckConstraint("reserved >= 0", name="ck_stock_reserved_nonneg"),
        sa.CheckConstraint("reserved <= quantity", name="ck_stock_reserved_lte_quantity"),
    )

    # receipts
    op.create_table(
        "receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(50), nullable=False, unique=True),
        sa.Column("supplier", sa.String(255), nullable=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "READY", "DONE", "CANCELLED", name="receiptstatus"), nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # receipt_lines
    op.create_table(
        "receipt_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("receipt_id", sa.Integer(), sa.ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("expected_qty", sa.Float(), nullable=False),
        sa.Column("received_qty", sa.Float(), nullable=False, server_default="0"),
    )

    # deliveries
    op.create_table(
        "deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(50), nullable=False, unique=True),
        sa.Column("customer", sa.String(255), nullable=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "WAITING", "READY", "PICKING", "PACKING", "DONE", "CANCELLED", name="deliverystatus"), nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # delivery_lines
    op.create_table(
        "delivery_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("delivery_id", sa.Integer(), sa.ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("requested_qty", sa.Float(), nullable=False),
        sa.Column("delivered_qty", sa.Float(), nullable=False, server_default="0"),
    )

    # transfers
    op.create_table(
        "transfers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(50), nullable=False, unique=True),
        sa.Column("src_location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("dst_location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "READY", "DONE", "CANCELLED", name="transferstatus"), nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # transfer_lines
    op.create_table(
        "transfer_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transfer_id", sa.Integer(), sa.ForeignKey("transfers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
    )

    # stock_adjustments
    op.create_table(
        "stock_adjustments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(50), nullable=False, unique=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("counted_qty", sa.Float(), nullable=False),
        sa.Column("recorded_qty", sa.Float(), nullable=False),
        sa.Column("delta", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "DONE", "CANCELLED", name="adjustmentstatus"), nullable=False, server_default="DRAFT"),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # stock_movements
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("movement_type", sa.Enum("RECEIPT", "DELIVERY", "TRANSFER_OUT", "TRANSFER_IN", "ADJUSTMENT", name="movementtype"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("reference", sa.String(100), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Indexes
    op.create_index("ix_stock_movements_product_id", "stock_movements", ["product_id"])
    op.create_index("ix_stock_movements_location_id", "stock_movements", ["location_id"])
    op.create_index("ix_stock_movements_created_at", "stock_movements", ["created_at"])
    op.create_index("ix_stock_movements_reference", "stock_movements", ["reference"])
    op.create_index("ix_inventory_stock_product_id", "inventory_stock", ["product_id"])
    op.create_index("ix_inventory_stock_location_id", "inventory_stock", ["location_id"])

    # Seed: default admin user (password: admin123)
    op.execute("""
        INSERT INTO users (email, full_name, hashed_password, role, is_active)
        VALUES ('admin@stocksense.com', 'Admin User', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ADMIN', true)
    """)

    # Seed: categories
    op.execute("""
        INSERT INTO categories (name, description) VALUES
        ('Electronics', 'Electronic components and devices'),
        ('Furniture', 'Office and warehouse furniture'),
        ('Raw Materials', 'Basic materials for production'),
        ('Consumables', 'Day-to-day consumable items')
    """)

    # Seed: units of measure
    op.execute("""
        INSERT INTO units_of_measure (name, abbreviation) VALUES
        ('Unit', 'pcs'),
        ('Kilogram', 'kg'),
        ('Liter', 'L'),
        ('Meter', 'm'),
        ('Box', 'box')
    """)

    # Seed: warehouse + location
    op.execute("""
        INSERT INTO warehouses (name, code, address) VALUES
        ('Main Warehouse', 'WH01', '123 Industrial Area, Hyderabad'),
        ('Secondary Warehouse', 'WH02', '456 Storage Zone, Hyderabad')
    """)
    op.execute("""
        INSERT INTO locations (warehouse_id, name, code, description)
        SELECT w.id, 'Zone A', 'A01', 'Primary storage zone'
        FROM warehouses w WHERE w.code = 'WH01'
    """)
    op.execute("""
        INSERT INTO locations (warehouse_id, name, code, description)
        SELECT w.id, 'Zone B', 'B01', 'Secondary storage zone'
        FROM warehouses w WHERE w.code = 'WH01'
    """)
    op.execute("""
        INSERT INTO locations (warehouse_id, name, code, description)
        SELECT w.id, 'Zone A', 'A01', 'Primary storage zone'
        FROM warehouses w WHERE w.code = 'WH02'
    """)


def downgrade() -> None:
    op.drop_table("stock_movements")
    op.drop_table("stock_adjustments")
    op.drop_table("transfer_lines")
    op.drop_table("transfers")
    op.drop_table("delivery_lines")
    op.drop_table("deliveries")
    op.drop_table("receipt_lines")
    op.drop_table("receipts")
    op.drop_table("inventory_stock")
    op.drop_table("locations")
    op.drop_table("warehouses")
    op.drop_table("products")
    op.drop_table("units_of_measure")
    op.drop_table("categories")
    op.drop_table("otp_tokens")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS receiptstatus")
    op.execute("DROP TYPE IF EXISTS deliverystatus")
    op.execute("DROP TYPE IF EXISTS transferstatus")
    op.execute("DROP TYPE IF EXISTS adjustmentstatus")
    op.execute("DROP TYPE IF EXISTS movementtype")
