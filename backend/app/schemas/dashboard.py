from pydantic import BaseModel

class DashboardKPIs(BaseModel):
    total_products_in_stock: int
    low_stock_or_out_of_stock: int
    pending_receipts: int
    pending_deliveries: int
    internal_transfers_scheduled: int
