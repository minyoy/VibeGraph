import { useState } from 'react'
import { api } from '../services/api'
import GraphPathView from './GraphPathView'

export default function RecommendationList({ tasteProfile, onRecommendations }) {
  const [candidates, setCandidates] = useState([])
  const [explained, setExplained] = useState(null)
  const [recStatus, setRecStatus] = useState('idle')
  const [explainStatus, setExplainStatus] = useState('idle')
  const [error, setError] = useState(null)

  async function fetchRecommendations() {
    setRecStatus('loading')
    setError(null)
    try {
      const data = await api.getRecommendations('user_default', 10)
      setCandidates(data)
      setRecStatus('success')
    } catch (e) {
      setRecStatus('error')
      setError(e.message)
    }
  }

  async function explainWithAI() {
    if (!candidates.length) return
    setExplainStatus('loading')
    setError(null)
    try {
      const result = await api.explainRecommendations('user_default', candidates, tasteProfile)
      setExplained(result)
      setExplainStatus('success')
      onRecommendations && onRecommendations(result)
    } catch (e) {
      setExplainStatus('error')
      setError(e.message)
    }
  }

  const tracks = explained?.tracks ?? candidates

  return (
    <section className="card space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-lg font-bold">추천 결과</h2>
        <div className="flex gap-2">
          <button onClick={fetchRecommendations} disabled={recStatus === 'loading'} className="btn-secondary text-sm py-1.5 px-4">
            {recStatus === 'loading' ? '불러오는 중...' : 'Graph 추천 생성'}
          </button>
          {candidates.length > 0 && (
            <button onClick={explainWithAI} disabled={explainStatus === 'loading'} className="btn-primary text-sm py-1.5 px-4">
              {explainStatus === 'loading' ? 'AI 분석 중...' : 'AI 추천 이유 생성'}
            </button>
          )}
        </div>
      </div>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {explained && (
        <div className="bg-apple-pink/10 border border-apple-pink/30 rounded-xl p-4 space-y-1">
          <p className="font-semibold text-apple-pink">{explained.playlistName}</p>
          <p className="text-sm text-apple-muted">{explained.explanation}</p>
        </div>
      )}

      {tracks.length > 0 && (
        <ul className="space-y-3">
          {tracks.map((track, i) => (
            <li key={track.id || i} className="flex gap-3 p-3 bg-apple-dark rounded-xl border border-apple-border">
              <span className="text-apple-pink font-mono text-sm w-5 flex-shrink-0 pt-0.5">{i + 1}</span>
              <div className="min-w-0 flex-1 space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-sm">{track.title}</p>
                    <p className="text-apple-muted text-xs">{track.artist}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="badge bg-apple-border text-apple-muted">{track.genre}</span>
                    <span className="badge bg-green-500/20 text-green-400">
                      {typeof track.score === 'number' ? track.score.toFixed(1) : track.score}
                    </span>
                  </div>
                </div>
                <GraphPathView path={track.graphPath} />
                {track.reason && (
                  <p className="text-apple-muted text-xs italic">{track.reason}</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {recStatus === 'success' && tracks.length === 0 && (
        <p className="text-apple-muted text-sm text-center py-4">
          추천 결과가 없습니다. 더 많은 플레이리스트를 동기화해 보세요.
        </p>
      )}
    </section>
  )
}
