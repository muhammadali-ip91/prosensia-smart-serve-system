import { useState, useEffect } from 'react'
import { HiOutlineWifi } from 'react-icons/hi'

export default function OfflineBanner() {
	const [isOffline, setIsOffline] = useState(!navigator.onLine)

	useEffect(() => {
		const handleOnline = () => setIsOffline(false)
		const handleOffline = () => setIsOffline(true)

		window.addEventListener('online', handleOnline)
		window.addEventListener('offline', handleOffline)

		return () => {
			window.removeEventListener('online', handleOnline)
			window.removeEventListener('offline', handleOffline)
		}
	}, [])

	if (!isOffline) return null

	return (
		<div className="bg-red-600 text-white text-center py-2 px-4 text-sm font-medium flex items-center justify-center space-x-2">
			<HiOutlineWifi className="w-4 h-4" />
			<span>You are offline. Some features may not work.</span>
		</div>
	)
}
