import { useState, useRef, useEffect } from 'react'
import { useNotification } from '../../hooks/useNotification'
import NotificationDropdown from './NotificationDropdown'
import { HiOutlineBell } from 'react-icons/hi'

export default function NotificationBell() {
	const { unreadCount } = useNotification()
	const [isOpen, setIsOpen] = useState(false)
	const dropdownRef = useRef(null)

	// Close dropdown on outside click
	useEffect(() => {
		function handleClick(e) {
			if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
				setIsOpen(false)
			}
		}
		document.addEventListener('mousedown', handleClick)
		return () => document.removeEventListener('mousedown', handleClick)
	}, [])

	return (
		<div className="relative" ref={dropdownRef}>
			<button
				onClick={() => setIsOpen(!isOpen)}
				className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
			>
				<HiOutlineBell className="w-6 h-6" />
				{unreadCount > 0 && (
					<span className="absolute -top-1 -right-1 bg-accent-red text-white text-xs w-5 h-5 flex items-center justify-center rounded-full font-bold animate-pulse">
						{unreadCount > 9 ? '9+' : unreadCount}
					</span>
				)}
			</button>

			{isOpen && <NotificationDropdown onClose={() => setIsOpen(false)} />}
		</div>
	)
}
