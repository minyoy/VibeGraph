import { useState } from 'react'
import { api } from '../services/api'
import Header from '../components/Header'
import AppleMusicLogin from '../components/AppleMusicLogin'
import PlaylistSelector from '../components/PlaylistSelector'
import TasteAnalysis from '../components/TasteAnalysis'
import RecommendationList from '../components/RecommendationList'
import CreatedPlaylistCard from '../components/CreatedPlaylistCard'

const USER_ID = 'user_default'

// appState: disconnected → connected → playlistSelected → synced → analyzed → recommended → explained → created

export default function Dashboard() {
  const [appState, setAppState] = useState('disconnected')
  const [musicUserToken, setMusicUserToken] = useState(null)
  const [selectedPlaylists, setSelectedPlaylists] = useState([])
  const [syncResult, setSyncResult] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [explanation, setExplanation] = useState(null)
  const [selectedTracks, setSelectedTracks] = useState([])
  const [createdPlaylist, setCreatedPlaylist] = useState(null)
  const [playlistName, setPlaylistName] = useState('VibeGraph Mix')

  const [loading, setLoading] = useState({})
  const [errors, setErrors] = useState({})

  function setLoad(key, val) { setLoading((p) => ({ ...p, [key]: val })) }
  function setErr(key, val) { setErrors((p) => ({ ...p, [key]: val })) }

  function handleConnected(token) {
    setMusicUserToken(token)
    setAppState('connected')
  }

  function handlePlaylistsSelected(playlists) {
    setSelectedPlaylists(playlists)
    if (playlists.length > 0 && appState === 'connected') {
      setAppState('playlistSelected')
    } else if (playlists.length === 0 && appState === 'playlistSelected') {
      setAppState('connected')
    }
  }

  async function handleSync() {
    setLoad('sync', true)
    setErr('sync', null)
    try {
      const result = await api.syncGraph(USER_ID, selectedPlaylists, musicUserToken)
      setSyncResult(result)
      setAppState('synced')
    } catch (e) {
      setErr('sync', e.message)
    } finally {
      setLoad('sync', false)
    }
  }

  async function handleAnalyze() {
    setLoad('analyze', true)
    setErr('analyze', null)
    try {
      const result = await api.getAnalysis(USER_ID)
      setAnalysis(result)
      setAppState('analyzed')
    } catch (e) {
      setErr('analyze', e.message)
    } finally {
      setLoad('analyze', false)
    }
  }

  async function handleRecommend() {
    setLoad('recommend', true)
    setErr('recommend', null)
    try {
      const result = await api.getRecommendations(USER_ID, 10)
      setRecommendations(result)
      setAppState('recommended')
    } catch (e) {
      setErr('recommend', e.message)
    } finally {
      setLoad('recommend', false)
    }
  }

  async function handleExplain() {
    setLoad('explain', true)
    setErr('explain', null)
    try {
      const result = await api.explainRecommendations(USER_ID, recommendations, analysis)
      setExplanation(result)
      setPlaylistName(result.playlistName)
      setAppState('explained')
    } catch (e) {
      setErr('explain', e.message)
    } finally {
      setLoad('explain', false)
    }
  }

  function handleTrackSelect(track) {
    setSelectedTracks((prev) => {
      const exists = prev.some((t) => t.id === track.id)
      return exists ? prev.filter((t) => t.id !== track.id) : [...prev, track]
    })
  }

  async function handleCreatePlaylist() {
    if (!selectedTracks.length) return
    setLoad('create', true)
    setErr('create', null)
    try {
      const result = await api.createPlaylist(
        USER_ID,
        playlistName,
        selectedTracks.map((t) => t.id),
        musicUserToken,
      )
      setCreatedPlaylist(result)
      setAppState('created')
    } catch (e) {
      setErr('create', e.message)
    } finally {
      setLoad('create', false)
    }
  }

  const stateOrder = ['disconnected', 'connected', 'playlistSelected', 'synced', 'analyzed', 'recommended', 'explained', 'created']
  const stateIndex = (s) => stateOrder.indexOf(s)
  const past = (s) => stateIndex(appState) >= stateIndex(s)

  return (
    <div className="min-h-screen bg-gray-50">
      <Header appState={appState} />

      <main className="max-w-2xl mx-auto px-4 py-8 space-y-6">

        {/* 1. Connect */}
        {appState === 'disconnected' && (
          <AppleMusicLogin onConnected={handleConnected} />
        )}

        {/* Connected badge */}
        {past('connected') && appState !== 'disconnected' && (
          <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-xl p-3">
            <span className="text-green-500">●</span>
            <span className="text-sm text-green-700 font-medium">Connected to Apple Music</span>
          </div>
        )}

        {/* 2. Select Playlists */}
        {past('connected') && (
          <PlaylistSelector
            musicUserToken={musicUserToken}
            onSelected={handlePlaylistsSelected}
          />
        )}

        {/* 3. Sync */}
        {past('playlistSelected') && (
          <section className="bg-white rounded-2xl p-6 shadow">
            <h2 className="text-lg font-semibold mb-2">3. Sync to Graph DB</h2>
            <p className="text-sm text-gray-500 mb-4">
              {selectedPlaylists.length} playlist(s) selected
            </p>
            {syncResult && (
              <div className="mb-4 p-3 bg-green-50 rounded-xl text-sm text-green-700">
                ✓ Synced — {syncResult.nodesCreated} nodes, {syncResult.relationshipsCreated} relationships created
              </div>
            )}
            {errors.sync && (
              <p className="mb-3 text-red-500 text-sm bg-red-50 p-3 rounded-lg">{errors.sync}</p>
            )}
            <button
              onClick={handleSync}
              disabled={loading.sync || !selectedPlaylists.length}
              className="bg-gray-900 text-white px-5 py-2.5 rounded-xl font-medium disabled:opacity-40 hover:bg-gray-700 transition-colors"
            >
              {loading.sync ? 'Syncing...' : 'Sync to Neo4j'}
            </button>
          </section>
        )}

        {/* 4. Analyze */}
        {past('synced') && (
          <section className="bg-white rounded-2xl p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">4. Taste Analysis</h2>
            {errors.analyze && (
              <p className="mb-3 text-red-500 text-sm bg-red-50 p-3 rounded-lg">{errors.analyze}</p>
            )}
            {!analysis && (
              <button
                onClick={handleAnalyze}
                disabled={loading.analyze}
                className="bg-purple-600 text-white px-5 py-2.5 rounded-xl font-medium disabled:opacity-40 hover:bg-purple-700 transition-colors"
              >
                {loading.analyze ? 'Analyzing...' : 'Analyze My Taste'}
              </button>
            )}
            {analysis && <TasteAnalysis analysis={analysis} />}
          </section>
        )}

        {/* 5. Recommend */}
        {past('analyzed') && (
          <section className="bg-white rounded-2xl p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">5. Graph Recommendations</h2>
            {errors.recommend && (
              <p className="mb-3 text-red-500 text-sm bg-red-50 p-3 rounded-lg">{errors.recommend}</p>
            )}
            {!recommendations.length && (
              <button
                onClick={handleRecommend}
                disabled={loading.recommend}
                className="bg-blue-600 text-white px-5 py-2.5 rounded-xl font-medium disabled:opacity-40 hover:bg-blue-700 transition-colors"
              >
                {loading.recommend ? 'Finding recommendations...' : 'Get Recommendations'}
              </button>
            )}
          </section>
        )}

        {/* 6. Explain */}
        {past('recommended') && recommendations.length > 0 && (
          <section className="bg-white rounded-2xl p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">6. AI Explanation</h2>
            {errors.explain && (
              <p className="mb-3 text-red-500 text-sm bg-red-50 p-3 rounded-lg">{errors.explain}</p>
            )}
            {!explanation && (
              <button
                onClick={handleExplain}
                disabled={loading.explain}
                className="bg-orange-500 text-white px-5 py-2.5 rounded-xl font-medium disabled:opacity-40 hover:bg-orange-600 transition-colors"
              >
                {loading.explain ? 'Generating explanations...' : 'Generate AI Reasons'}
              </button>
            )}
          </section>
        )}

        {/* Recommendation List (shown after recommend step) */}
        {recommendations.length > 0 && (
          <RecommendationList
            recommendations={recommendations}
            explanation={explanation}
            onSelect={handleTrackSelect}
            selected={selectedTracks}
          />
        )}

        {/* 7. Create Playlist */}
        {past('recommended') && recommendations.length > 0 && (
          <section className="bg-white rounded-2xl p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">7. Create Playlist</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Playlist Name</label>
              <input
                type="text"
                value={playlistName}
                onChange={(e) => setPlaylistName(e.target.value)}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-apple"
              />
            </div>
            <p className="text-sm text-gray-500 mb-4">
              {selectedTracks.length} track(s) selected
            </p>
            {errors.create && (
              <p className="mb-3 text-red-500 text-sm bg-red-50 p-3 rounded-lg">{errors.create}</p>
            )}
            <button
              onClick={handleCreatePlaylist}
              disabled={loading.create || !selectedTracks.length}
              className="bg-apple text-white px-5 py-2.5 rounded-xl font-medium disabled:opacity-40 hover:bg-red-600 transition-colors"
            >
              {loading.create ? 'Creating...' : 'Create in Apple Music'}
            </button>
          </section>
        )}

        {/* Created */}
        {createdPlaylist && <CreatedPlaylistCard result={createdPlaylist} />}

      </main>
    </div>
  )
}
