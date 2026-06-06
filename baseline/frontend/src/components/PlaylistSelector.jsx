import { useState, useEffect } from 'react'
import { api } from '../services/api'

export default function PlaylistSelector({ musicUserToken, onSelect, onSync }) {
  const [playlists, setPlaylists] = useState([])
  const [selected, setSelected] = useState([])
  const [status, setStatus] = useState('idle')
  const [syncStatus, setSyncStatus] = useState('idle')
  const [syncMsg, setSyncMsg] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => {
    loadPlaylists()
  }, [musicUserToken])

  async function loadPlaylists() {
    setStatus('loading')
    setError(null)
    try {
      const res = await api.getPlaylists(musicUserToken)
      setPlaylists(res.data || [])
      setStatus('success')
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  function toggle(pl) {
    setSelected((prev) =>
      prev.find((p) => p.id === pl.id)
        ? prev.filter((p) => p.id !== pl.id)
        : [...prev, pl]
    )
  }

  async function handleSync() {
    if (!selected.length) return
    setSyncStatus('loading')
    setSyncMsg('')
    try {
      const res = await api.syncGraph('user_default', selected, musicUserToken)
      setSyncStatus('success')
      setSyncMsg(`동기화 완료: ${res.nodesCreated}개 노드, ${res.relationshipsCreated}개 관계 생성`)
      onSync && onSync(selected)
    } catch (e) {
      setSyncStatus('error')
      setSyncMsg(e.message)
    }
  }

  return (
    <section className="card space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">플레이리스트 선택</h2>
        <button onClick={loadPlaylists} className="text-apple-pink text-sm hover:underline">
          새로고침
        </button>
      </div>

      {status === 'loading' && <p className="text-apple-muted text-sm">플레이리스트 불러오는 중...</p>}
      {status === 'error' && <p className="text-red-400 text-sm">{error}</p>}

      {status === 'success' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-72 overflow-y-auto pr-1">
          {playlists.map((pl) => {
            const isSelected = selected.find((p) => p.id === pl.id)
            return (
              <button
                key={pl.id}
                onClick={() => toggle(pl)}
                className={`flex items-center gap-3 p-3 rounded-xl border transition-all text-left ${
                  isSelected
                    ? 'border-apple-pink bg-apple-pink/10'
                    : 'border-apple-border hover:border-apple-muted'
                }`}
              >
                {pl.artwork ? (
                  <img src={pl.artwork} alt="" className="w-10 h-10 rounded-lg flex-shrink-0" />
                ) : (
                  <div className="w-10 h-10 rounded-lg bg-apple-border flex-shrink-0 flex items-center justify-center text-apple-muted text-xs">
                    ♪
                  </div>
                )}
                <div className="min-w-0">
                  <p className="font-medium text-sm truncate">{pl.name}</p>
                  <p className="text-apple-muted text-xs">
                    {typeof pl.trackCount === 'number' ? `${pl.trackCount}곡` : '곡 수 확인 필요'}
                  </p>
                </div>
                {isSelected && <span className="ml-auto text-apple-pink">✓</span>}
              </button>
            )
          })}
        </div>
      )}

      {selected.length > 0 && (
        <div className="pt-2 border-t border-apple-border">
          <p className="text-sm text-apple-muted mb-3">{selected.length}개 플레이리스트 선택됨</p>
          <button
            onClick={handleSync}
            disabled={syncStatus === 'loading'}
            className="btn-primary w-full"
          >
            {syncStatus === 'loading' ? 'Neo4j에 동기화 중...' : 'Graph DB에 동기화'}
          </button>
          {syncMsg && (
            <p className={`mt-2 text-sm ${syncStatus === 'success' ? 'text-green-400' : 'text-red-400'}`}>
              {syncMsg}
            </p>
          )}
        </div>
      )}
    </section>
  )
}
