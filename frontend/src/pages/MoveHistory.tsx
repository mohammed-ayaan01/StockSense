import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { movementsApi } from '../api'
import { LoadingSpinner, EmptyState } from '../components/States'
import StatusBadge from '../components/StatusBadge'

export default function MoveHistory() {
  const [typeFilter, setTypeFilter] = useState('')
  const [refFilter, setRefFilter] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 50

  const { data: movements = [], isLoading } = useQuery({
    queryKey: ['movements', typeFilter, refFilter, offset],
    queryFn: () => movementsApi.list({ movement_type: typeFilter || undefined, reference: refFilter || undefined, limit, offset }).then(r => r.data),
  })

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Move History</h1>
        <p className="text-sm text-gray-500 mt-1">Complete audit log of all stock movements</p>
      </div>

      <div className="flex gap-3 mb-5">
        <input className="form-input max-w-xs" placeholder="Search reference..." value={refFilter} onChange={e => { setRefFilter(e.target.value); setOffset(0) }} />
        <select className="form-select max-w-xs" value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setOffset(0) }}>
          <option value="">All Types</option>
          {['RECEIPT','DELIVERY','TRANSFER_OUT','TRANSFER_IN','ADJUSTMENT'].map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      <div className="card p-0 overflow-hidden">
        {isLoading ? <LoadingSpinner /> : movements.length === 0 ? <EmptyState message="No movements found" /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="table-th">Type</th>
                  <th className="table-th">Reference</th>
                  <th className="table-th">Product</th>
                  <th className="table-th">Location</th>
                  <th className="table-th text-right">Quantity</th>
                  <th className="table-th">Notes</th>
                  <th className="table-th">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {movements.map((m: any) => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="table-td"><StatusBadge status={m.movement_type} /></td>
                    <td className="table-td font-mono text-xs font-semibold">{m.reference}</td>
                    <td className="table-td text-sm">Product #{m.product_id}</td>
                    <td className="table-td text-sm">Loc #{m.location_id}</td>
                    <td className={`table-td text-right font-bold ${m.quantity > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {m.quantity > 0 ? '+' : ''}{m.quantity}
                    </td>
                    <td className="table-td text-xs text-gray-500 max-w-xs truncate">{m.notes || '—'}</td>
                    <td className="table-td text-xs text-gray-500">{new Date(m.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <p className="text-sm text-gray-500">Showing {offset + 1}–{offset + movements.length}</p>
        <div className="flex gap-2">
          <button onClick={() => setOffset(Math.max(0, offset - limit))} disabled={offset === 0} className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-40">Previous</button>
          <button onClick={() => setOffset(offset + limit)} disabled={movements.length < limit} className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-40">Next</button>
        </div>
      </div>
    </div>
  )
}
