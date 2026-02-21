const CACHE_PREFIX = 'prosensia_cache_'
const DEFAULT_TTL = 5 * 60 * 1000 // 5 minutes

const cacheService = {
	set(key, data, ttl = DEFAULT_TTL) {
		const cacheData = {
			data,
			expiry: Date.now() + ttl
		}
		localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(cacheData))
	},

	get(key) {
		try {
			const raw = localStorage.getItem(CACHE_PREFIX + key)
			if (!raw) return null

			const cacheData = JSON.parse(raw)

			if (Date.now() > cacheData.expiry) {
				localStorage.removeItem(CACHE_PREFIX + key)
				return null
			}

			return cacheData.data
		} catch {
			return null
		}
	},

	remove(key) {
		localStorage.removeItem(CACHE_PREFIX + key)
	},

	clearAll() {
		Object.keys(localStorage)
			.filter(key => key.startsWith(CACHE_PREFIX))
			.forEach(key => localStorage.removeItem(key))
	},
}

export default cacheService
