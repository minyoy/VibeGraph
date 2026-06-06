import GraphPathView from './GraphPathView'

export default function RecommendationList({ recommendations, explanation, onSelect, selected }) {
  if (!recommendations?.length) return null

  return (
    <section className="bg-white rounded-2xl p-6 shadow">
      <h2 className="text-lg font-semibold mb-1">5. Recommended Tracks</h2>
      {explanation && (
        <div className="mb-4 p-3 bg-purple-50 rounded-xl">
          <p className="text-sm font-medium text-purple-800">"{explanation.playlistName}"</p>
          <p className="text-xs text-purple-600 mt-1">{explanation.explanation}</p>
        </div>
      )}
      <p className="text-gray-500 text-sm mb-4">
        Select tracks to add to your new playlist ({selected.length} selected)
      </p>
      <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
        {recommendations.map((track) => {
          const isSelected = selected.some((t) => t.id === track.id)
          const displayTrack = explanation?.tracks?.find((t) => t.id === track.id) || track

          return (
            <button
              key={track.id}
              onClick={() => onSelect(track)}
              className={`w-full text-left p-3 rounded-xl border-2 transition-all ${
                isSelected ? 'border-apple bg-red-50' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="font-medium text-sm truncate">{track.title}</p>
                  <p className="text-gray-500 text-xs">{track.artist} · {track.genre}</p>
                  <GraphPathView path={track.graphPath} />
                  {displayTrack.reason && (
                    <p className="text-xs text-gray-600 mt-1 italic">{displayTrack.reason}</p>
                  )}
                </div>
                <div className="flex-shrink-0 text-right">
                  <span className="text-xs font-medium text-apple">Score: {track.score}</span>
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </section>
  )
}
