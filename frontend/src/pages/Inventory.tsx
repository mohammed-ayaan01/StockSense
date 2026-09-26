import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { inventoryApi, warehousesApi } from '../api'
import { LoadingSpinner, EmptyState } from '../components/States'

export default function Inventory() {
  const [whFilter, setWhFilter] = useState('')
  const [search, setSearch] = useState('')

  const { data: warehouses = [] } = useQuery({ queryKey: ['warehouses'], queryFn: () => warehousesApi.list().then(r => r.data) })
  const { data: stock = [], isLoading } = useQuery({
    queryKey: ['inventory', whFilter],
    queryFn: () => inventoryApi.list(whFilter ? { warehouse_id: whFilter } : undefined).then(r => r.data),
  })

  const filtered = stock.filter((s: any) =>
    !search || s.product_name?.toLowerCase().includes(search.toLowerCase()) || s.product_sku?.toLowerCase().includes(search.toLowerCase())
  )

  const getRowClass = (s: any) => {
    if (s.quantity === 0) return 'bg-red-50'
    if (s.reorder_threshold && s.quantity <= s.reorder_threshold) return 'bg-amber-50'
    return ''
  }

  const getStockStatus = (s: any) => {
    if (s.quantity === 0) return <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-medium">Out of Stock</span>
    if (s.reorder_threshold && s.quantity <= s.reorder_threshold) return <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 font-medium">Low Stock</span>
    return <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-medium">Normal</span>
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-gray-900">Inventory</h1><p className="text-sm text-gray-500 mt-1">Current stock levels</p></div>
      </div>
      <div className="flex gap-3 mb-5">
        <input className="form-input max-w-xs" placeholder="Search product..." value={search} onChange={e => setSearch(e.target.value)} />
        <select className="form-select max-w-xs" value={whFilter} onChange={e => setWhFilter(e.target.value)}>
          <option value="">All Warehouses</option>
          {warehouses.map((w: any) => <option key={w.id} value={w.id}>{w.name}</option>)}
        </select>
      </div>
      <div className="card p-0 overflow-hidden">
        {isLoading ? <LoadingSpinner /> : filtered.length === 0 ? <EmptyState message="No stock records found" /> : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="table-th">Product</th>
                  <th className="table-th">SKU</th>
                  <th className="table-th">Location</th>
                  <th className="table-th">Warehouse</th>
                  <th className="table-th text-right">On Hand</th>
                  <th className="table-th text-right">Reserved</th>
                  <th className="table-th text-right">Available</th>
                  <th className="table-th">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((s: any) => (
                  <tr key={s.id} className={`hover:bg-gray-50 ${getRowClass(s)}`}>
                    <td className="table-td font-medium">{s.product_name}</td>
                    <td className="table-td font-mono text-xs text-gray-500">{s.product_sku}</td>
                    <td className="table-td">{s.location_name} <span className="text-xs text-gray-400">({s.location_code})</span></td>
                    <td className="table-td">{s.warehouse_name}</td>
                    <td className="table-td text-right font-semibold">{s.quantity} <span className="text-xs text-gray-400">{s.uom}</span></td>
                    <td className="table-td text-right text-gray-500">{s.reserved}</td>
                    <td className={`table-td text-right font-semibold ${s.free_to_use === 0 ? 'text-red-600' : s.reorder_threshold && s.free_to_use <= s.reorder_threshold ? 'text-amber-600' : 'text-emerald-600'}`}>{s.free_to_use}</td>
                    <td className="table-td">{getStockStatus(s)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
