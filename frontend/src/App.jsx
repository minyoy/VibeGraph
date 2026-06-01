import { useState, useEffect } from 'react'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import { unauthorize } from './services/musicKit'

const TOKEN_KEY = 'vg_music_user_token'

export default function App() {
  const [musicUserToken, setMusicUserToken] = useState(() => sessionStorage.getItem(TOKEN_KEY))

  function handleLogin(token) {
    sessionStorage.setItem(TOKEN_KEY, token)
    setMusicUserToken(token)
  }

  async function handleLogout() {
    await unauthorize().catch(() => {})
    sessionStorage.removeItem(TOKEN_KEY)
    setMusicUserToken(null)
  }

  return (
    <div className="min-h-screen bg-apple-dark">
      <Header isConnected={!!musicUserToken} onLogout={handleLogout} />
      <main>
        <Dashboard musicUserToken={musicUserToken} onLogin={handleLogin} />
      </main>
    </div>
  )
}
