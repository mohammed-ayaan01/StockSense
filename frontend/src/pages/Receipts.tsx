import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { receiptsApi, productsApi, warehousesApi } from '../api'
import { LoadingSpinner, EmptyState } from '../components/States'
import StatusBadge from '../components/StatusBadge'
import { Plus, X, Trash2 } from 'lucide-react'

export default function Receipts() {
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ supplier: '', location_id: '', notes: '' })
  const [lines, setLines] = useState<{product_id: string, expected_qty: string}[]>([{ product_id: '', expected_qty: '' }])

  const { data: receipts = [], isLoading } = useQuery({
    queryKey: ['receipts', statusFilter],
    queryFn: () => receiptsApi.list(statusFilter ? { status: statusFilter } : undefined).then(r => r.data),
  })
  const { data: products = [] } = useQuery({ queryKey: ['products'], queryFn: () => productsApi.list().then(r => r.data) })
  const { data: locations = [] } = useQuery({ queryKey: ['locations'], queryFn: () => warehousesApi.listLocations().then(r => r.data) })

  const createMut = useMutation({
    mutationFn: (d: any) => receiptsApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['receipts'] }); qc.invalidateQueries({ queryKey: ['dashboard-kpis'] }); toast.success('Receipt created'); setShowForm(false); resetForm() },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed to create receipt'),
  })
  const confirmMut = useMutation({
    mutationFn: (id: number) => receiptsApi.confirm(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['receipts'] }); qc.invalidateQueries({ queryKey: ['dashboard-kpis'] }); toast.success('Receipt confirmed') },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })
  const validateMut = useMutation({
    mutationFn: (id: number) => receiptsApi.validate(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['receipts'] }); qc.invalidateQueries({ queryKey: ['inventory'] }); qc.invalidateQueries({ queryKey: ['dashboard-kpis'] }); qc.invalidateQueries({ queryKey: ['recent-movements'] }); toast.success('Receipt validated — stock increased!') },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed to validate'),
  })
  const cancelMut = useMutation({
    mutationFn: (id: number) => receiptsApi.cancel(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['receipts'] }); qc.invalidateQueries({ queryKey: ['dashboard-kpis'] }); toast.success('Receipt cancelled') },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })

  const resetForm = () => { setForm({ supplier: '', location_id: '', notes: '' }); setLines([{ product_id: '', expected_qty: '' }]) }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.location_id) { toast.error('Select a destination location'); return }
    if (lines.some(l => !l.product_id || !l.expected_qty || Number(l.expected_qty) <= 0)) { toast.error('All lines need a product and quantity > 0'); return }
    createMut.mutate({ ...form, location_id: Number(form.location_id), lines: lines.map(l => ({ product_id: Number(l.product_id), expected_qty: Number(l.expected_qty) })) })
  }

  const addLine = () => setLines(ls => [...ls, { product_id: '', expected_qty: '' }])
  const removeLine = (i: number) => setLines(ls => ls.filter((_, idx) => idx !== i))
  const updateLine = (i: number, field: string, val: string) => setLines(ls => ls.map((l, idx) => idx === i ? {...l, [field]: val} : l))

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-gray-900">Receipts</h1><p className="text-sm text-gray-500 mt-1">Incoming stock operations</p></div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2"><Plus size={16} />New Receipt</button>
      </div>

      <div className="flex gap-3 mb-5">
        <select className="form-select max-w-xs" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          {['DRAFT','READY','DONE','CANCELLED'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="card p-0 overflow-hidden">
        {isLoading ? <LoadingSpinner /> : receipts.length === 0 ? <EmptyState message="No receipts found" /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="table-th">Reference</th>
                  <th className="table-th">Supplier</th>
                  <th className="table-th">Lines</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Created</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {receipts.map((r: any) => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="table-td font-mono font-semibold text-blue-700">{r.reference}</td>
                    <td className="table-td">{r.supplier || '—'}</td>
                    <td className="table-td">{r.lines?.length ?? 0} lines</td>
                    <td className="table-td"><StatusBadge status={r.status} /></td>
                    <td className="table-td text-gray-500 text-xs">{new Date(r.created_at).toLocaleDateString()}</td>
                    <td className="table-td">
                      <div className="flex gap-2 flex-wrap">
                        {r.status === 'DRAFT' && <button onClick={() => confirmMut.mutate(r.id)} className="text-xs btn-secondary py-1 px-2">Confirm</button>}
                        {(r.status === 'READY' || r.status === 'DRAFT') && <button onClick={() => { if(confirm('Validate receipt and increase stock?')) validateMut.mutate(r.id) }} className="text-xs btn-success py-1 px-2">Validate</button>}
                        {(r.status === 'DRAFT' || r.status === 'READY') && <button onClick={() => cancelMut.mutate(r.id)} className="text-xs btn-danger py-1 px-2">Cancel</button>}
                        {r.status === 'DONE' && <span className="text-xs text-emerald-600 font-medium">✓ Completed {r.done_at ? new Date(r.done_at).toLocaleDateString() : ''}</span>}
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
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-5"><h2 className="text-lg font-bold">New Receipt</h2><button onClick={() => { setShowForm(false); resetForm() }}><X size={20} /></button></div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><label className="form-label">Supplier (optional)</label><input className="form-input" value={form.supplier} onChange={e => setForm(f => ({...f, supplier: e.target.value}))} /></div>
                <div><label className="form-label">Destination Location</label>
                  <select className="form-select" value={form.location_id} onChange={e => setForm(f => ({...f, location_id: e.target.value}))} required>
                    <option value="">Select location</option>
                    {locations.map((l: any) => <option key={l.id} value={l.id}>{l.warehouse?.name} → {l.name} ({l.code})</option>)}
                  </select>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="form-label mb-0">Product Lines</label>
                  <button type="button" onClick={addLine} className="text-sm text-blue-600 hover:underline">+ Add line</button>
                </div>
                {lines.map((line, i) => (
                  <div key={i} className="flex gap-3 mb-2 items-center">
                    <select className="form-select flex-1" value={line.product_id} onChange={e => updateLine(i, 'product_id', e.target.value)} required>
                      <option value="">Select product</option>
                      {products.map((p: any) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                    </select>
                    <input type="number" step="0.01" min="0.01" className="form-input w-28" placeholder="Qty" value={line.expected_qty} onChange={e => updateLine(i, 'expected_qty', e.target.value)} required />
                    {lines.length > 1 && <button type="button" onClick={() => removeLine(i)} className="text-red-400 hover:text-red-600"><Trash2 size={16} /></button>}
                  </div>
                ))}
              </div>
              <div><label className="form-label">Notes</label><textarea className="form-input" value={form.notes} onChange={e => setForm(f => ({...f, notes: e.target.value}))} rows={2} /></div>
              <div className="flex justify-end gap-3"><button type="button" onClick={() => { setShowForm(false); resetForm() }} className="btn-secondary">Cancel</button><button type="submit" className="btn-primary" disabled={createMut.isPending}>Create Receipt</button></div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
