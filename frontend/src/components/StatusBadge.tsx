interface Props {
  status: string
}

const statusMap: Record<string, { label: string; classes: string }> = {
  DRAFT: { label: 'Draft', classes: 'bg-gray-100 text-gray-700' },
  READY: { label: 'Ready', classes: 'bg-blue-100 text-blue-700' },
  WAITING: { label: 'Waiting', classes: 'bg-amber-100 text-amber-700' },
  PICKING: { label: 'Picking', classes: 'bg-indigo-100 text-indigo-700' },
  PACKING: { label: 'Packing', classes: 'bg-purple-100 text-purple-700' },
  DONE: { label: 'Done', classes: 'bg-emerald-100 text-emerald-700' },
  CANCELLED: { label: 'Cancelled', classes: 'bg-red-100 text-red-700' },
  RECEIPT: { label: 'Receipt', classes: 'bg-blue-100 text-blue-700' },
  DELIVERY: { label: 'Delivery', classes: 'bg-red-100 text-red-700' },
  TRANSFER_OUT: { label: 'Transfer Out', classes: 'bg-orange-100 text-orange-700' },
  TRANSFER_IN: { label: 'Transfer In', classes: 'bg-green-100 text-green-700' },
  ADJUSTMENT: { label: 'Adjustment', classes: 'bg-purple-100 text-purple-700' },
}

export default function StatusBadge({ status }: Props) {
  const config = statusMap[status] || { label: status, classes: 'bg-gray-100 text-gray-700' }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.classes}`}>
      {config.label}
    </span>
  )
}
