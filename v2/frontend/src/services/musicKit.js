const DEV_TOKEN = import.meta.env.VITE_APPLE_MUSIC_DEVELOPER_TOKEN

export async function initMusicKit() {
  await new Promise((resolve) => {
    if (window.MusicKit) return resolve()
    document.addEventListener('musickitloaded', resolve, { once: true })
  })

  await window.MusicKit.configure({
    developerToken: DEV_TOKEN,
    app: { name: 'VibeGraph', build: '2.0.0' },
  })

  return window.MusicKit.getInstance()
}

export async function authorize(instance) {
  const token = await instance.authorize()
  return token
}

export function getMusicInstance() {
  return window.MusicKit?.getInstance() ?? null
}
