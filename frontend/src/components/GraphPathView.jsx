export default function GraphPathView({ path }) {
  if (!path) return null
  const nodes = path.split('→').map((n) => n.trim())

  return (
    <div className="flex items-center flex-wrap gap-1 text-xs mt-1">
      {nodes.map((node, i) => (
        <span key={i} className="flex items-center gap-1">
          <span className="badge bg-apple-border text-apple-muted">{node}</span>
          {i < nodes.length - 1 && <span className="text-apple-muted">→</span>}
        </span>
      ))}
    </div>
  )
}
