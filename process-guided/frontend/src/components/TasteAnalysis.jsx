export default function TasteAnalysis({ analysis }) {
  if (!analysis) return null

  return (
    <section className="bg-white rounded-2xl p-6 shadow">
      <h2 className="text-lg font-semibold mb-4">4. Your Taste Profile</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Top Artists</h3>
          <ul className="space-y-1">
            {analysis.topArtists.slice(0, 5).map((a) => (
              <li key={a.name} className="flex items-center justify-between text-sm">
                <span className="truncate">{a.name}</span>
                <span className="text-gray-400 ml-2 flex-shrink-0">{a.count}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-2">Top Genres</h3>
          <ul className="space-y-1">
            {analysis.topGenres.slice(0, 5).map((g) => (
              <li key={g.name} className="flex items-center justify-between text-sm">
                <span className="truncate">{g.name}</span>
                <span className="text-gray-400 ml-2 flex-shrink-0">{g.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {analysis.detectedTaste.map((t) => (
          <span key={t} className="px-3 py-1 bg-purple-100 text-purple-700 text-xs rounded-full font-medium">
            {t}
          </span>
        ))}
        {analysis.moodTags.map((m) => (
          <span key={m} className="px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
            {m}
          </span>
        ))}
      </div>
    </section>
  )
}
