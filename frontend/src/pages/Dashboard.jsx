import { useState } from 'react'
import AppleMusicLogin from '../components/AppleMusicLogin'
import PlaylistSelector from '../components/PlaylistSelector'
import TasteAnalysis from '../components/TasteAnalysis'
import RecommendationList from '../components/RecommendationList'
import CreatedPlaylistCard from '../components/CreatedPlaylistCard'

export default function Dashboard({ musicUserToken, onLogin }) {
  const [synced, setSynced] = useState(false)
  const [tasteProfile, setTasteProfile] = useState(null)
  const [recommendations, setRecommendations] = useState(null)

  if (!musicUserToken) {
    return (
      <div className="max-w-lg mx-auto mt-20 px-4">
        <AppleMusicLogin onLogin={onLogin} />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <PlaylistSelector
        musicUserToken={musicUserToken}
        onSync={() => setSynced(true)}
      />

      {synced && (
        <TasteAnalysis onAnalysisReady={setTasteProfile} />
      )}

      {synced && (
        <RecommendationList
          tasteProfile={tasteProfile}
          onRecommendations={setRecommendations}
        />
      )}

      {recommendations && (
        <CreatedPlaylistCard
          recommendations={recommendations}
          musicUserToken={musicUserToken}
        />
      )}
    </div>
  )
}
