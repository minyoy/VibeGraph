const STEPS = [
  'Connect',
  'Select',
  'Sync',
  'Analyze',
  'Recommend',
  'Explain',
  'Create',
]

const STEP_INDEX = {
  disconnected: -1,
  connected: 0,
  playlistSelected: 1,
  synced: 2,
  analyzed: 3,
  recommended: 4,
  explained: 5,
  created: 6,
}

export default function Header({ appState }) {
  const current = STEP_INDEX[appState] ?? -1

  return (
    <header className="bg-black text-white px-6 py-4">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-apple mb-3">VibeGraph</h1>
        <div className="flex items-center gap-1 flex-wrap">
          {STEPS.map((step, i) => (
            <div key={step} className="flex items-center gap-1">
              <span
                className={`text-xs px-2 py-1 rounded-full ${
                  i <= current
                    ? 'bg-apple text-white'
                    : 'bg-gray-700 text-gray-400'
                }`}
              >
                {step}
              </span>
              {i < STEPS.length - 1 && (
                <span className="text-gray-600 text-xs">→</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </header>
  )
}
