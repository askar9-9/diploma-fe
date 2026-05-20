interface LoadingStateProps {
  className?: string
  label?: string
}

export function LoadingState({
  className = '',
  label = 'Загрузка...',
}: LoadingStateProps) {
  return (
    <div className={`flex items-center justify-center gap-3 rounded-xl border border-gray-700 bg-gray-800 px-6 py-10 ${className}`} role="status" aria-live="polite">
      <span aria-label={label} className="h-5 w-5 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" />
      <span className="text-sm font-medium text-gray-400">{label}</span>
    </div>
  )
}
