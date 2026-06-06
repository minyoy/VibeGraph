const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(method, path, { body, headers = {} } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...headers },
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export const api = {
  health: () => request('GET', '/health'),

  getPlaylists: (musicUserToken) =>
    request('GET', '/apple/playlists', {
      headers: { 'Music-User-Token': musicUserToken },
    }),

  getTracks: (playlistId, musicUserToken) =>
    request('GET', `/apple/playlists/${playlistId}/tracks`, {
      headers: { 'Music-User-Token': musicUserToken },
    }),

  syncGraph: (userId, playlists, musicUserToken) =>
    request('POST', '/graph/sync', {
      body: { userId, playlists },
      headers: { 'Music-User-Token': musicUserToken },
    }),

  getAnalysis: (userId) =>
    request('GET', `/analysis/${userId}`),

  getRecommendations: (userId, limit = 10) =>
    request('GET', `/recommendations/${userId}?limit=${limit}`),

  explainRecommendations: (userId, candidates, tasteProfile) =>
    request('POST', '/agent/explain', {
      body: { userId, candidates, tasteProfile },
    }),

  createPlaylist: (userId, playlistName, trackIds, musicUserToken) =>
    request('POST', '/apple/playlists/create', {
      body: { userId, playlistName, trackIds, musicUserToken },
    }),
}
