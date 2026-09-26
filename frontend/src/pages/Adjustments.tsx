import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { adjustmentsApi, productsApi, warehousesApi, inventoryApi } from '../api'
import { LoadingSpinner, EmptyState } from '../components/States'
import StatusBadge from '../components/StatusBadge'
import { Plus, X } from 'lucide-react'

export default function Adjustments() {
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ product_id: '', location_id: '', counted_qty: '', reason: '' })
  const [currentStock, setCurrentStock] = useState<number | null>(null)

  const { data: adjustments = [], isLoading } = useQuery({
    queryKey: ['adjustments', statusFilter],
    queryFn: () => adjustmentsApi.list(statusFilter ? { status: statusFilter } : undefined).then(r => r.data),
  })
  const { data: products = [] } = useQuery({ queryKey: ['products'], queryFn: () => productsApi.list().then(r => r.data) })
  const { data: locations = [] } = useQuery({ queryKey: ['locations'], queryFn: () => warehousesApi.listLocations().then(r => r.data) })

  const lookupStock = async (productId: string, locationId: string) => {
    if (!productId || !locationId) { setCurrentStock(null); return }
    try {
      const res = await inventoryApi.list({ product_id: productId, location_id: locationId })
      setCurrentStock(res.data[0]?.quantity ?? 0)
    } catch { setCurrentStock(0) }
  }

  const createMut = useMutation({
    mutationFn: (d: any) => adjustmentsApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['adjustments'] }); toast.success('Adjustment created'); setShowForm(false); resetForm() },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })
  const validateMut = useMutation({
    mutationFn: (id: number) => adjustmentsApi.validate(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['adjustments'] }); qc.invalidateQueries({ queryKey: ['inventory'] }); qc.invalidateQueries({ queryKey: ['recent-movements'] }); toast.success('Adjustment applied!') },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed', { duration: 6000 }),
  })
  const cancelMut = useMutation({
    mutationFn: (id: number) => adjustmentsApi.cancel(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['adjustments'] }); toast.success('Cancelled') },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })

  const resetForm = () => { setForm({ product_id: '', location_id: '', counted_qty: '', reason: '' }); setCurrentStock(null) }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.reason.trim()) { toast.error('Reason is required'); return }
    if (Number(form.counted_qty) < 0) { toast.error('Counted quantity cannot be negative'); return }
    createMut.mutate({ ...form, product_id: Number(form.product_id), location_id: Number(form.location_id), counted_qty: Number(form.counted_qty) })
  }

  const delta = form.counted_qty !== '' && currentStock !== null ? Number(form.counted_qty) - currentStock : null

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-gray-900">Stock Adjustments</h1><p className="text-sm text-gray-500 mt-1">Reconcile physical counts</p></div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2"><Plus size={16} />New Adjustment</button>
      </div>

      <div className="flex gap-3 mb-5">
        <select className="form-select max-w-xs" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          {['DRAFT','DONE','CANCELLED'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="card p-0 overflow-hidden">
        {isLoading ? <LoadingSpinner /> : adjustments.length === 0 ? <EmptyState message="No adjustments found" /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="table-th">Reference</th>
                  <th className="table-th text-right">Counted</th>
                  <th className="table-th text-right">Recorded</th>
                  <th className="table-th text-right">Delta</th>
                  <th className="table-th">Reason</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {adjustments.map((a: any) => (
                  <tr key={a.id} className="hover:bg-gray-50">
                    <td className="table-td font-mono font-semibold text-purple-700">{a.reference}</td>
                    <td className="table-td text-right font-medium">{a.counted_qty}</td>
                    <td className="table-td text-right text-gray-500">{a.recorded_qty}</td>
                    <td className={`table-td text-right font-bold ${a.delta > 0 ? 'text-emerald-600' : a.delta < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                      {a.delta > 0 ? '+' : ''}{a.delta}
                    </td>
                    <td className="table-td text-sm text-gray-600 max-w-xs truncate">{a.reason}</td>
                    <td className="table-td"><StatusBadge status={a.status} /></td>
                    <td className="table-td">
                      <div className="flex gap-2">
                        {a.status === 'DRAFT' && (
                          <><button onClick={() => { if(confirm('Apply adjustment to stock?')) validateMut.mutate(a.id) }} className="text-xs btn-success py-1 px-2">Apply</button>
                          <button onClick={() => cancelMut.mutate(a.id)} className="text-xs btn-danger py-1 px-2">Cancel</button></>
                        )}
                        {a.status === 'DONE' && <span className="text-xs text-emerald-600 font-medium">✓ Applied</span>}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5"><h2 className="text-lg font-bold">New Stock Adjustment</h2><button onClick={() => { setShowForm(false); resetForm() }}><X size={20} /></button></div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div><label className="form-label">Product</label>
                <select className="form-select" value={form.product_id} onChange={e => { setForm(f => ({...f, product_id: e.target.value})); lookupStock(e.target.value, form.location_id) }} required>
                  <option value="">Select product</option>
                  {products.map((p: any) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                </select>
              </div>
              <div><label className="form-label">Location</label>
                <select className="form-select" value={form.location_id} onChange={e => { setForm(f => ({...f, location_id: e.target.value})); lookupStock(form.product_id, e.target.value) }} required>
                  <option value="">Select location</option>
                  {locations.map((l: any) => <option key={l.id} value={l.id}>{l.warehouse?.name} → {l.name} ({l.code})</option>)}
                </select>
              </div>
              {currentStock !== null && <div className="bg-gray-50 rounded-lg p-3 text-sm"><span className="text-gray-500">Current recorded stock: </span><span className="font-bold text-gray-900">{currentStock}</span></div>}
              <div>
                <label className="form-label">Physically Counted Quantity</label>
                <input type="number" step="0.01" min="0" className="form-input" value={form.counted_qty} onChange={e => setForm(f => ({...f, counted_qty: e.target.value}))} required />
                {delta !== null && <p className={`text-sm mt-1 font-medium ${delta > 0 ? 'text-emerald-600' : delta < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                  Delta: {delta > 0 ? '+' : ''}{delta} (stock will be {delta > 0 ? 'increased' : delta < 0 ? 'decreased' : 'unchanged'})
                </p>}
              </div>
              <div><label className="form-label">Reason <span className="text-red-500">*</span></label><textarea className="form-input" value={form.reason} onChange={e => setForm(f => ({...f, reason: e.target.value}))} rows={3} required placeholder="e.g. Physical count discrepancy, damaged goods, cycle count" /></div>
              <div className="flex justify-end gap-3"><button type="button" onClick={() => { setShowForm(false); resetForm() }} className="btn-secondary">Cancel</button><button type="submit" className="btn-primary" disabled={createMut.isPending}>Create Adjustment</button></div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
