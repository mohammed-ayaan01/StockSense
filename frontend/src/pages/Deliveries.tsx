import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { deliveriesApi, productsApi, warehousesApi } from '../api'
import { LoadingSpinner, EmptyState } from '../components/States'
import StatusBadge from '../components/StatusBadge'
import { Plus, X, Trash2 } from 'lucide-react'

const ADVANCE_LABELS: Record<string, string> = {
  DRAFT: 'Confirm →',
  WAITING: 'Mark Ready →',
  READY: 'Start Picking →',
  PICKING: 'Start Packing →',
  PACKING: 'Validate & Deliver',
}

export default function Deliveries() {
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ customer: '', location_id: '', notes: '' })
  const [lines, setLines] = useState<{product_id: string, requested_qty: string}[]>([{ product_id: '', requested_qty: '' }])

  const { data: deliveries = [], isLoading } = useQuery({
    queryKey: ['deliveries', statusFilter],
    queryFn: () => deliveriesApi.list(statusFilter ? { status: statusFilter } : undefined).then(r => r.data),
  })
  const { data: products = [] } = useQuery({ queryKey: ['products'], queryFn: () => productsApi.list().then(r => r.data) })
  const { data: locations = [] } = useQuery({ queryKey: ['locations'], queryFn: () => warehousesApi.listLocations().then(r => r.data) })

  const createMut = useMutation({
    mutationFn: (d: any) => deliveriesApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['deliveries'] }); qc.invalidateQueries({ queryKey: ['dashboard-kpis'] }); toast.success('Delivery created'); setShowForm(false); resetForm() },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed to create delivery'),
  })
  const advanceMut = useMutation({
    mutationFn: (id: number) => deliveriesApi.advance(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deliveries'] })
      qc.invalidateQueries({ queryKey: ['inventory'] })
      qc.invalidateQueries({ queryKey: ['dashboard-kpis'] })
      qc.invalidateQueries({ queryKey: ['recent-movements'] })
      toast.success('Delivery advanced!')
    },
    onError: (e: any) => {
      const msg = e.response?.data?.detail || 'Failed to advance delivery'
      toast.error(msg, { duration: 6000 })
    },
  })
  const cancelMut = useMutation({
    mutationFn: (id: number) => deliveriesApi.cancel(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['deliveries'] }); qc.invalidateQueries({ queryKey: ['dashboard-kpis'] }); toast.success('Delivery cancelled') },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })

  const resetForm = () => { setForm({ customer: '', location_id: '', notes: '' }); setLines([{ product_id: '', requested_qty: '' }]) }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.location_id) { toast.error('Select a source location'); return }
    if (lines.some(l => !l.product_id || !l.requested_qty || Number(l.requested_qty) <= 0)) { toast.error('All lines need a product and quantity > 0'); return }
    createMut.mutate({ ...form, location_id: Number(form.location_id), lines: lines.map(l => ({ product_id: Number(l.product_id), requested_qty: Number(l.requested_qty) })) })
  }

  const addLine = () => setLines(ls => [...ls, { product_id: '', requested_qty: '' }])
  const removeLine = (i: number) => setLines(ls => ls.filter((_, idx) => idx !== i))
  const updateLine = (i: number, field: string, val: string) => setLines(ls => ls.map((l, idx) => idx === i ? {...l, [field]: val} : l))

  const handleAdvance = (d: any) => {
    if (d.status === 'PACKING') {
      if (!confirm('Validate delivery? This will deduct stock. Make sure quantities are available.')) return
    }
    advanceMut.mutate(d.id)
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-gray-900">Deliveries</h1><p className="text-sm text-gray-500 mt-1">Outgoing stock operations</p></div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2"><Plus size={16} />New Delivery</button>
      </div>

      <div className="flex gap-3 mb-5">
        <select className="form-select max-w-xs" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          {['DRAFT','WAITING','READY','PICKING','PACKING','DONE','CANCELLED'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="card p-0 overflow-hidden">
        {isLoading ? <LoadingSpinner /> : deliveries.length === 0 ? <EmptyState message="No deliveries found" /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="table-th">Reference</th>
                  <th className="table-th">Customer</th>
                  <th className="table-th">Lines</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Created</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {deliveries.map((d: any) => (
                  <tr key={d.id} className="hover:bg-gray-50">
                    <td className="table-td font-mono font-semibold text-purple-700">{d.reference}</td>
                    <td className="table-td">{d.customer || '—'}</td>
                    <td className="table-td">{d.lines?.length ?? 0} lines</td>
                    <td className="table-td"><StatusBadge status={d.status} /></td>
                    <td className="table-td text-gray-500 text-xs">{new Date(d.created_at).toLocaleDateString()}</td>
                    <td className="table-td">
                      <div className="flex gap-2 flex-wrap">
                        {ADVANCE_LABELS[d.status] && (
                          <button
                            onClick={() => handleAdvance(d)}
                            className={`text-xs py-1 px-2 ${d.status === 'PACKING' ? 'btn-success' : 'btn-secondary'}`}
                            disabled={advanceMut.isPending}
                          >
                            {ADVANCE_LABELS[d.status]}
                          </button>
                        )}
                        {!['DONE','CANCELLED'].includes(d.status) && (
                          <button onClick={() => cancelMut.mutate(d.id)} className="text-xs btn-danger py-1 px-2">Cancel</button>
                        )}
                        {d.status === 'DONE' && <span className="text-xs text-emerald-600 font-medium">✓ Delivered {d.done_at ? new Date(d.done_at).toLocaleDateString() : ''}</span>}
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
            <div className="flex items-center justify-between mb-5"><h2 className="text-lg font-bold">New Delivery</h2><button onClick={() => { setShowForm(false); resetForm() }}><X size={20} /></button></div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><label className="form-label">Customer (optional)</label><input className="form-input" value={form.customer} onChange={e => setForm(f => ({...f, customer: e.target.value}))} /></div>
                <div><label className="form-label">Source Location</label>
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
                    <input type="number" step="0.01" min="0.01" className="form-input w-28" placeholder="Qty" value={line.requested_qty} onChange={e => updateLine(i, 'requested_qty', e.target.value)} required />
                    {lines.length > 1 && <button type="button" onClick={() => removeLine(i)} className="text-red-400 hover:text-red-600"><Trash2 size={16} /></button>}
                  </div>
                ))}
              </div>
              <div><label className="form-label">Notes</label><textarea className="form-input" value={form.notes} onChange={e => setForm(f => ({...f, notes: e.target.value}))} rows={2} /></div>
              <div className="flex justify-end gap-3"><button type="button" onClick={() => { setShowForm(false); resetForm() }} className="btn-secondary">Cancel</button><button type="submit" className="btn-primary" disabled={createMut.isPending}>Create Delivery</button></div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
