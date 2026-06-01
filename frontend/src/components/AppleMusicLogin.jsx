import { useState } from 'react'
import { authorize } from '../services/musicKit'

export default function AppleMusicLogin({ onLogin }) {
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  async function handleLogin() {
    setStatus('loading')
    setError(null)
    try {
      const token = await authorize()
      setStatus('success')
      onLogin(token)
    } catch (e) {
      setStatus('error')
      setError(e.message)
    }
  }

  return (
    <section className="card flex flex-col items-center gap-6 py-12">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">VibeGraph에 오신 걸 환영합니다</h2>
        <p className="text-apple-muted text-sm max-w-sm">
          Apple Music 계정을 연결하면 플레이리스트를 분석하고 개인화 추천을 받을 수 있습니다.
        </p>
      </div>

      <button
        onClick={handleLogin}
        disabled={status === 'loading'}
        className="btn-primary flex items-center gap-2 text-base px-8 py-3"
      >
        {status === 'loading' ? (
          <>
            <Spinner />
            연결 중...
          </>
        ) : (
          <>
            <AppleIcon />
            Apple Music으로 로그인
          </>
        )}
      </button>

      {status === 'error' && (
        <p className="text-red-400 text-sm text-center max-w-xs">
          {error || 'Apple Music 연결에 실패했습니다.'}
        </p>
      )}
    </section>
  )
}

function AppleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
    </svg>
  )
}

function Spinner() {
  return (
    <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  )
}
