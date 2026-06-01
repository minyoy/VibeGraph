import { useState } from 'react'
import { api } from '../services/api'

export default function TasteAnalysis({ onAnalysisReady }) {
  const [analysis, setAnalysis] = useState(null)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  async function runAnalysis() {
    setStatus('loading')
    setError(null)
    try {
      const data = await api.getTasteAnalysis('user_default')
      setAnalysis(data)
      setStatus('success')
      onAnalysisReady && onAnalysisReady(data)
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  return (
    <section className="card space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">취향 분석</h2>
        <button onClick={runAnalysis} disabled={status === 'loading'} className="btn-primary text-sm py-1.5 px-4">
          {status === 'loading' ? '분석 중...' : '분석 실행'}
        </button>
      </div>

      {status === 'error' && <p className="text-red-400 text-sm">{error}</p>}

      {analysis && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <h3 className="text-apple-muted text-xs uppercase tracking-widest mb-2">Top Artists</h3>
            <ul className="space-y-1.5">
              {analysis.topArtists.slice(0, 5).map((a, i) => (
                <li key={i} className="flex items-center gap-2 text-sm">
                  <span className="text-apple-pink font-mono w-4">{i + 1}</span>
                  <span className="flex-1 truncate">{a.name}</span>
                  <span className="text-apple-muted text-xs">{a.count}곡</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-apple-muted text-xs uppercase tracking-widest mb-2">Top Genres</h3>
            <ul className="space-y-1.5">
              {analysis.topGenres.slice(0, 5).map((g, i) => (
                <li key={i} className="flex items-center gap-2 text-sm">
                  <span className="text-apple-pink font-mono w-4">{i + 1}</span>
                  <span className="flex-1 truncate">{g.name}</span>
                  <span className="text-apple-muted text-xs">{g.count}곡</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-apple-muted text-xs uppercase tracking-widest mb-2">Detected Taste</h3>
            <div className="flex flex-wrap gap-2">
              {analysis.detectedTaste.map((t, i) => (
                <span key={i} className="badge bg-apple-pink/20 text-apple-pink">{t}</span>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-apple-muted text-xs uppercase tracking-widest mb-2">Mood Tags</h3>
            <div className="flex flex-wrap gap-2">
              {analysis.moodTags.map((m, i) => (
                <span key={i} className="badge bg-purple-500/20 text-purple-300">{m}</span>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
