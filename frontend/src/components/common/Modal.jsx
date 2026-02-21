import { useEffect } from 'react'
import { HiOutlineX } from 'react-icons/hi'

export default function Modal({ isOpen, onClose, title, children, size = 'md' }) {
	useEffect(() => {
		if (isOpen) {
			document.body.style.overflow = 'hidden'
		} else {
			document.body.style.overflow = 'unset'
		}
		return () => { document.body.style.overflow = 'unset' }
	}, [isOpen])

	if (!isOpen) return null

	const sizes = {
		sm: 'max-w-md',
		md: 'max-w-lg',
		lg: 'max-w-2xl',
		xl: 'max-w-4xl',
	}

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4">
			{/* Backdrop */}
			<div
				className="absolute inset-0 bg-black/50 backdrop-blur-sm"
				onClick={onClose}
			></div>

			{/* Modal Content */}
			<div className={`relative bg-white rounded-2xl shadow-xl ${sizes[size]} w-full animate-slide-in max-h-[90vh] flex flex-col`}>
				{/* Header */}
				<div className="flex items-center justify-between p-6 border-b border-gray-100">
					<h2 className="text-xl font-bold text-gray-900">{title}</h2>
					<button
						onClick={onClose}
						className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
					>
						<HiOutlineX className="w-5 h-5" />
					</button>
				</div>

				{/* Body */}
				<div className="p-4 sm:p-6 overflow-y-auto">
					{children}
				</div>
			</div>
		</div>
	)
}
