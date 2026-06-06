import { useState, useEffect } from 'react'
import { api } from '../services/api'

export default function PlaylistSelector({ musicUserToken, onSelected }) {
  const [playlists, setPlaylists] = useState([])
  const [selected, setSelected] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await api.getPlaylists(musicUserToken)
        setPlaylists(res.data)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [musicUserToken])

  function toggle(playlist) {
    setSelected((prev) => {
      const exists = prev.find((p) => p.id === playlist.id)
      const next = exists ? prev.filter((p) => p.id !== playlist.id) : [...prev, playlist]
      onSelected(next)
      return next
    })
  }

  if (loading) return (
    <section className="bg-white rounded-2xl p-6 shadow">
      <h2 className="text-lg font-semibold mb-4">2. Select Playlists</h2>
      <p className="text-gray-500 animate-pulse">Loading playlists...</p>
    </section>
  )

  return (
    <section className="bg-white rounded-2xl p-6 shadow">
      <h2 className="text-lg font-semibold mb-1">2. Select Playlists</h2>
      <p className="text-gray-500 text-sm mb-4">
        Select one or more playlists to analyze ({selected.length} selected)
      </p>
      {error && (
        <p className="text-red-500 text-sm bg-red-50 p-3 rounded-lg mb-4">{error}</p>
      )}
      {playlists.length === 0 && !error && (
        <p className="text-gray-400 text-sm">No playlists found in your library.</p>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-80 overflow-y-auto pr-1">
        {playlists.map((pl) => {
          const isSelected = selected.some((p) => p.id === pl.id)
          return (
            <button
              key={pl.id}
              onClick={() => toggle(pl)}
              className={`flex items-center gap-3 p-3 rounded-xl border-2 text-left transition-all ${
                isSelected
                  ? 'border-apple bg-red-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {pl.artwork ? (
                <img src={pl.artwork} alt={pl.name} className="w-12 h-12 rounded-lg object-cover flex-shrink-0" />
              ) : (
                <div className="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center flex-shrink-0">
                  <span className="text-gray-400 text-xl">♪</span>
                </div>
              )}
              <div className="min-w-0">
                <p className="font-medium text-sm truncate">{pl.name}</p>
                <p className="text-gray-400 text-xs">{pl.trackCount} tracks</p>
              </div>
            </button>
          )
        })}
      </div>
    </section>
  )
}
