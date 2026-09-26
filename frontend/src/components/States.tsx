interface Props {
  message?: string
}

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
  )
}

export function ErrorState({ message = 'Something went wrong. Please try again.' }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="text-red-500 text-4xl mb-3">⚠️</div>
      <p className="text-gray-600">{message}</p>
    </div>
  )
}

export function EmptyState({ message = 'No data found.' }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="text-gray-300 text-5xl mb-3">📦</div>
      <p className="text-gray-500">{message}</p>
    </div>
  )
}
