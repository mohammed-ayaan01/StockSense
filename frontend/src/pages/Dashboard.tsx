import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../api'
import { LoadingSpinner, ErrorState } from '../components/States'
import StatusBadge from '../components/StatusBadge'
import { Package, AlertTriangle, ClipboardList, Truck, ArrowLeftRight } from 'lucide-react'

interface KPIs {
  total_products_in_stock: number
  low_stock_or_out_of_stock: number
  pending_receipts: number
  pending_deliveries: number
  internal_transfers_scheduled: number
}

const kpiCards = [
  { key: 'total_products_in_stock', label: 'Total Products in Stock', icon: Package, color: 'blue' },
  { key: 'low_stock_or_out_of_stock', label: 'Low / Out of Stock', icon: AlertTriangle, color: 'amber' },
  { key: 'pending_receipts', label: 'Pending Receipts', icon: ClipboardList, color: 'green' },
  { key: 'pending_deliveries', label: 'Pending Deliveries', icon: Truck, color: 'purple' },
  { key: 'internal_transfers_scheduled', label: 'Transfers Scheduled', icon: ArrowLeftRight, color: 'indigo' },
] as const

const colorMap: Record<string, string> = {
  blue: 'bg-blue-50 text-blue-600',
  amber: 'bg-amber-50 text-amber-600',
  green: 'bg-emerald-50 text-emerald-600',
  purple: 'bg-purple-50 text-purple-600',
  indigo: 'bg-indigo-50 text-indigo-600',
}

export default function Dashboard() {
  const { data: kpis, isLoading: kLoading, isError: kError } = useQuery<KPIs>({
    queryKey: ['dashboard-kpis'],
    queryFn: () => dashboardApi.kpis().then(r => r.data),
    refetchInterval: 15000,
  })

  const { data: movements = [] } = useQuery<any[]>({
    queryKey: ['recent-movements'],
    queryFn: () => dashboardApi.recentMovements().then(r => r.data),
    refetchInterval: 15000,
  })

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Live inventory overview</p>
      </div>

      {kLoading ? <LoadingSpinner /> : kError ? <ErrorState /> : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          {kpiCards.map(({ key, label, icon: Icon, color }) => (
            <div key={key} className="card">
              <div className={`inline-flex p-2.5 rounded-lg mb-3 ${colorMap[color]}`}>
                <Icon size={20} />
              </div>
              <p className="text-3xl font-bold text-gray-900">{kpis?.[key as keyof KPIs] ?? 0}</p>
              <p className="text-sm text-gray-500 mt-1">{label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Movements</h2>
        {movements.length === 0 ? (
          <p className="text-gray-400 text-sm py-8 text-center">No movements yet. Complete a receipt, delivery, or transfer to see them here.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-gray-100">
                <tr>
                  <th className="table-th">Type</th>
                  <th className="table-th">Reference</th>
                  <th className="table-th text-right">Quantity</th>
                  <th className="table-th">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {movements.map((m: any) => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="table-td"><StatusBadge status={m.type} /></td>
                    <td className="table-td font-mono text-xs">{m.reference}</td>
                    <td className={`table-td text-right font-semibold ${m.quantity > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {m.quantity > 0 ? '+' : ''}{m.quantity}
                    </td>
                    <td className="table-td text-gray-500">{new Date(m.created_at).toLocaleString()}</td>
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
