import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { productsApi } from '../api'
import { LoadingSpinner, ErrorState, EmptyState } from '../components/States'
import { Plus, Pencil, X } from 'lucide-react'

export default function Products() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editProduct, setEditProduct] = useState<any>(null)
  const [form, setForm] = useState({ name: '', sku: '', category_id: '', uom_id: '', unit_cost: '', reorder_threshold: '', description: '' })

  const { data: products = [], isLoading, isError } = useQuery({
    queryKey: ['products', search, catFilter],
    queryFn: () => productsApi.list({ search: search || undefined, category_id: catFilter || undefined }).then(r => r.data),
  })
  const { data: categories = [] } = useQuery({ queryKey: ['categories'], queryFn: () => productsApi.listCategories().then(r => r.data) })
  const { data: uoms = [] } = useQuery({ queryKey: ['uoms'], queryFn: () => productsApi.listUom().then(r => r.data) })

  const createMut = useMutation({
    mutationFn: (d: any) => productsApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['products'] }); toast.success('Product created'); closeForm() },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })
  const updateMut = useMutation({
    mutationFn: ({ id, d }: any) => productsApi.update(id, d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['products'] }); toast.success('Product updated'); closeForm() },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })

  const closeForm = () => { setShowForm(false); setEditProduct(null); setForm({ name: '', sku: '', category_id: '', uom_id: '', unit_cost: '', reorder_threshold: '', description: '' }) }

  const openEdit = (p: any) => {
    setEditProduct(p)
    setForm({ name: p.name, sku: p.sku, category_id: String(p.category_id), uom_id: String(p.uom_id), unit_cost: String(p.unit_cost), reorder_threshold: p.reorder_threshold ? String(p.reorder_threshold) : '', description: p.description || '' })
    setShowForm(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload = { ...form, category_id: Number(form.category_id), uom_id: Number(form.uom_id), unit_cost: Number(form.unit_cost), reorder_threshold: form.reorder_threshold ? Number(form.reorder_threshold) : null }
    if (editProduct) updateMut.mutate({ id: editProduct.id, d: payload })
    else createMut.mutate(payload)
  }

  const toggleActive = (p: any) => updateMut.mutate({ id: p.id, d: { is_active: !p.is_active } })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-sm text-gray-500 mt-1">{products.length} products</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} />
          New Product
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-5">
        <input className="form-input max-w-xs" placeholder="Search name or SKU..." value={search} onChange={e => setSearch(e.target.value)} />
        <select className="form-select max-w-xs" value={catFilter} onChange={e => setCatFilter(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        {isLoading ? <LoadingSpinner /> : isError ? <ErrorState /> : products.length === 0 ? <EmptyState message="No products found. Create your first product!" /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="table-th">Name</th>
                  <th className="table-th">SKU</th>
                  <th className="table-th">Category</th>
                  <th className="table-th">UoM</th>
                  <th className="table-th text-right">Unit Cost</th>
                  <th className="table-th text-right">Reorder At</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {products.map((p: any) => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="table-td font-medium">{p.name}</td>
                    <td className="table-td font-mono text-xs text-gray-500">{p.sku}</td>
                    <td className="table-td">{p.category?.name || '—'}</td>
                    <td className="table-td">{p.unit_of_measure?.abbreviation || '—'}</td>
                    <td className="table-td text-right">₹{p.unit_cost.toFixed(2)}</td>
                    <td className="table-td text-right">{p.reorder_threshold ?? '—'}</td>
                    <td className="table-td">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${p.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'}`}>
                        {p.is_active ? 'Active' : 'Archived'}
                      </span>
                    </td>
                    <td className="table-td">
                      <div className="flex gap-2">
                        <button onClick={() => openEdit(p)} className="text-blue-600 hover:text-blue-800"><Pencil size={14} /></button>
                        <button onClick={() => toggleActive(p)} className={`text-xs font-medium ${p.is_active ? 'text-red-500 hover:text-red-700' : 'text-emerald-600 hover:text-emerald-800'}`}>
                          {p.is_active ? 'Archive' : 'Activate'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold">{editProduct ? 'Edit Product' : 'New Product'}</h2>
              <button onClick={closeForm}><X size={20} /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div><label className="form-label">Name</label><input className="form-input" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required /></div>
                <div><label className="form-label">SKU</label><input className="form-input" value={form.sku} onChange={e => setForm(f => ({...f, sku: e.target.value}))} required disabled={!!editProduct} /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="form-label">Category</label>
                  <select className="form-select" value={form.category_id} onChange={e => setForm(f => ({...f, category_id: e.target.value}))} required>
                    <option value="">Select category</option>
                    {categories.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div><label className="form-label">Unit of Measure</label>
                  <select className="form-select" value={form.uom_id} onChange={e => setForm(f => ({...f, uom_id: e.target.value}))} required>
                    <option value="">Select UoM</option>
                    {uoms.map((u: any) => <option key={u.id} value={u.id}>{u.name} ({u.abbreviation})</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="form-label">Unit Cost</label><input type="number" step="0.01" min="0" className="form-input" value={form.unit_cost} onChange={e => setForm(f => ({...f, unit_cost: e.target.value}))} /></div>
                <div><label className="form-label">Reorder Threshold</label><input type="number" step="0.01" min="0" className="form-input" value={form.reorder_threshold} onChange={e => setForm(f => ({...f, reorder_threshold: e.target.value}))} placeholder="Optional" /></div>
              </div>
              <div><label className="form-label">Description</label><textarea className="form-input" value={form.description} onChange={e => setForm(f => ({...f, description: e.target.value}))} rows={2} /></div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={closeForm} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary" disabled={createMut.isPending || updateMut.isPending}>
                  {editProduct ? 'Save Changes' : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
