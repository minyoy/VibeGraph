const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => request('/health'),

  getPlaylists: (musicUserToken) =>
    request('/apple/playlists', {
      headers: { 'Music-User-Token': musicUserToken },
    }),

  getPlaylistTracks: (playlistId, musicUserToken) =>
    request(`/apple/playlists/${playlistId}/tracks`, {
      headers: { 'Music-User-Token': musicUserToken },
    }),

  syncGraph: (userId, playlists, musicUserToken) =>
    request('/graph/sync', {
      method: 'POST',
      headers: { 'Music-User-Token': musicUserToken },
      body: JSON.stringify({ userId, playlists }),
    }),

  getTasteAnalysis: (userId) => request(`/analysis/${userId}`),

  getRecommendations: (userId, limit = 10) =>
    request(`/recommendations/${userId}?limit=${limit}`),

  explainRecommendations: (userId, candidates, tasteProfile) =>
    request('/agent/explain', {
      method: 'POST',
      body: JSON.stringify({ userId, candidates, tasteProfile }),
    }),

  createPlaylist: (userId, playlistName, trackIds, musicUserToken) =>
    request('/apple/playlists/create', {
      method: 'POST',
      body: JSON.stringify({ userId, playlistName, trackIds, musicUserToken }),
    }),
}
