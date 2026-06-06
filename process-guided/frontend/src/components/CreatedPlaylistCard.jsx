export default function CreatedPlaylistCard({ result }) {
  if (!result) return null

  return (
    <section className="bg-white rounded-2xl p-6 shadow border-2 border-green-200">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-2xl">
          ✓
        </div>
        <div>
          <h2 className="text-lg font-semibold text-green-700">Playlist Created!</h2>
          <p className="text-sm text-gray-600">{result.message}</p>
          <p className="text-xs text-gray-400 mt-1">Playlist ID: {result.playlistId}</p>
        </div>
      </div>
      <p className="mt-3 text-sm text-gray-500">
        Open Apple Music to find your new playlist.
      </p>
    </section>
  )
}
