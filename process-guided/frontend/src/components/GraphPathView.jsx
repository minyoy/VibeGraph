export default function GraphPathView({ path }) {
  if (!path) return null
  const parts = path.split(' -> ')

  return (
    <div className="flex flex-wrap items-center gap-1 mt-1">
      {parts.map((part, i) => (
        <span key={i} className="flex items-center gap-1">
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{part}</span>
          {i < parts.length - 1 && <span className="text-gray-300 text-xs">→</span>}
        </span>
      ))}
    </div>
  )
}
