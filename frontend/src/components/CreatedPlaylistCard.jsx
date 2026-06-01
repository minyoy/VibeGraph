import { useState } from 'react'
import { api } from '../services/api'

export default function CreatedPlaylistCard({ recommendations, musicUserToken }) {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [customName, setCustomName] = useState(recommendations?.playlistName || 'VibeGraph Mix')

  const trackIds = (recommendations?.tracks ?? []).map((t) => t.id).filter(Boolean)

  async function handleCreate() {
    if (!trackIds.length) return
    setStatus('loading')
    setError(null)
    try {
      const res = await api.createPlaylist('user_default', customName, trackIds, musicUserToken)
      setResult(res)
      setStatus('success')
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  if (!recommendations?.tracks?.length) return null

  return (
    <section className="card space-y-4">
      <h2 className="text-lg font-bold">Apple Music 플레이리스트 생성</h2>

      <div className="flex gap-2">
        <input
          type="text"
          value={customName}
          onChange={(e) => setCustomName(e.target.value)}
          className="flex-1 bg-apple-dark border border-apple-border rounded-xl px-4 py-2.5 text-sm text-apple-text focus:outline-none focus:border-apple-pink"
          placeholder="플레이리스트 이름"
        />
        <button onClick={handleCreate} disabled={status === 'loading' || !trackIds.length} className="btn-primary whitespace-nowrap">
          {status === 'loading' ? '생성 중...' : 'Apple Music에 생성'}
        </button>
      </div>

      <p className="text-apple-muted text-xs">{trackIds.length}개 곡이 포함됩니다</p>

      {status === 'success' && result && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
          <p className="text-green-400 font-semibold">플레이리스트 생성 완료</p>
          <p className="text-apple-muted text-sm mt-1">{result.message}</p>
        </div>
      )}

      {status === 'error' && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}
    </section>
  )
}
