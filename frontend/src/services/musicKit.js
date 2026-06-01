const DEVELOPER_TOKEN = import.meta.env.VITE_APPLE_MUSIC_DEVELOPER_TOKEN

let musicKitInstance = null

export async function initMusicKit() {
  if (!DEVELOPER_TOKEN) {
    throw new Error('VITE_APPLE_MUSIC_DEVELOPER_TOKEN is not set')
  }
  await window.MusicKit.configure({
    developerToken: DEVELOPER_TOKEN,
    app: { name: 'VibeGraph', build: '1.0.0' },
  })
  musicKitInstance = window.MusicKit.getInstance()
  return musicKitInstance
}

export async function authorize() {
  if (!musicKitInstance) {
    await initMusicKit()
  }
  const musicUserToken = await musicKitInstance.authorize()
  return musicUserToken
}

export async function unauthorize() {
  if (musicKitInstance) {
    await musicKitInstance.unauthorize()
  }
}

export function getMusicKit() {
  return musicKitInstance
}

export function isAuthorized() {
  return musicKitInstance?.isAuthorized ?? false
}
