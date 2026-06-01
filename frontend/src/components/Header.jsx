export default function Header({ isConnected, onLogout }) {
  return (
    <header className="border-b border-apple-border bg-apple-dark/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-apple-pink text-2xl font-bold tracking-tight">Vibe</span>
          <span className="text-apple-text text-2xl font-bold tracking-tight">Graph</span>
        </div>
        {isConnected && (
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-sm text-green-400">
              <span className="w-2 h-2 rounded-full bg-green-400 inline-block" />
              Apple Music 연결됨
            </span>
            <button onClick={onLogout} className="btn-secondary text-sm py-1.5 px-3">
              연결 해제
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
