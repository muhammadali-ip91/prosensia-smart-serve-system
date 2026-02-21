import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { useCart } from '../../hooks/useCart'
import NotificationBell from '../notification/NotificationBell'
import ConnectionIndicator from './ConnectionIndicator'
import { getInitials } from '../../utils/helpers'
import {
	HiOutlineHome, HiOutlineShoppingCart, HiOutlineClipboardList,
	HiOutlineUser, HiOutlineLogout, HiOutlineMenu, HiOutlineX
} from 'react-icons/hi'

export default function Navbar() {
	const { user, logout } = useAuth()
	const { getCartCount } = useCart()
	const navigate = useNavigate()
	const location = useLocation()
	const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

	const cartCount = getCartCount()

	const handleLogout = async () => {
		await logout()
		navigate('/login')
	}

	// Navigation links based on role
	const getNavLinks = () => {
		switch (user?.role) {
			case 'engineer':
				return [
					{ path: '/menu', label: 'Menu', icon: HiOutlineHome },
					{ path: '/orders', label: 'My Orders', icon: HiOutlineClipboardList },
					{ path: '/trivia', label: 'Trivia', icon: null },
				]
			case 'kitchen':
				return [
					{ path: '/kitchen', label: 'Dashboard', icon: HiOutlineHome },
				]
			case 'runner':
				return [
					{ path: '/runner', label: 'Deliveries', icon: HiOutlineHome },
				]
			case 'admin':
				return [
					{ path: '/admin', label: 'Dashboard', icon: HiOutlineHome },
					{ path: '/admin/menu', label: 'Menu', icon: null },
					{ path: '/admin/users', label: 'Users', icon: null },
				]
			default:
				return []
		}
	}

	const navLinks = getNavLinks()
	const isActive = (path) => location.pathname === path

	return (
		<nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div className="flex justify-between h-16">
					{/* Left: Logo + Nav Links */}
					<div className="flex items-center space-x-3 sm:space-x-8 min-w-0">
						{/* Logo */}
						<Link to="/" className="flex items-center space-x-2 min-w-0">
							<div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
								<span className="text-white font-bold text-sm">PS</span>
							</div>
							<span className="font-bold text-lg text-gray-900 hidden sm:block truncate">
								Smart-Serve
							</span>
						</Link>

						{/* Desktop Nav Links */}
						<div className="hidden md:flex items-center space-x-1">
							{navLinks.map(link => (
								<Link
									key={link.path}
									to={link.path}
									className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
										isActive(link.path)
											? 'bg-primary-50 text-primary-700'
											: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
									}`}
								>
									{link.label}
								</Link>
							))}
						</div>
					</div>

					{/* Right: Cart + Notifications + Profile */}
					<div className="flex items-center space-x-1 sm:space-x-3">
						<div className="hidden sm:block">
							<ConnectionIndicator />
						</div>

						{/* Cart (Engineer only) */}
						{user?.role === 'engineer' && (
							<Link
								to="/cart"
								className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
							>
								<HiOutlineShoppingCart className="w-6 h-6" />
								{cartCount > 0 && (
									<span className="absolute -top-1 -right-1 bg-accent-red text-white text-xs w-5 h-5 flex items-center justify-center rounded-full font-bold">
										{cartCount > 9 ? '9+' : cartCount}
									</span>
								)}
							</Link>
						)}

						{/* Notifications */}
						<div className="hidden sm:block">
							<NotificationBell />
						</div>

						{/* Profile Dropdown */}
						<div className="flex items-center space-x-1 sm:space-x-2">
							<Link
								to="/profile"
								className="flex items-center space-x-2 px-1 sm:px-3 py-1.5 rounded-lg hover:bg-gray-50 transition-colors"
							>
								<div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold">
									{getInitials(user?.name)}
								</div>
								<span className="text-sm font-medium text-gray-700 hidden lg:block max-w-28 truncate">
									{user?.name}
								</span>
							</Link>

							<button
								onClick={handleLogout}
								className="p-2 text-gray-400 hover:text-accent-red hover:bg-red-50 rounded-lg transition-colors"
								title="Logout"
							>
								<HiOutlineLogout className="w-5 h-5" />
							</button>
						</div>

						{/* Mobile Menu Button */}
						<button
							onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
							className="md:hidden p-2 text-gray-600 hover:bg-gray-50 rounded-lg"
						>
							{mobileMenuOpen ? (
								<HiOutlineX className="w-6 h-6" />
							) : (
								<HiOutlineMenu className="w-6 h-6" />
							)}
						</button>
					</div>
				</div>
			</div>

			{/* Mobile Menu */}
			{mobileMenuOpen && (
				<div className="md:hidden border-t border-gray-200 bg-white animate-slide-in">
					<div className="px-4 py-3 space-y-1">
						<div className="pb-2 mb-2 border-b border-gray-100">
							<div className="flex items-center justify-between">
								<p className="text-sm font-medium text-gray-700 truncate">{user?.name}</p>
								<ConnectionIndicator />
							</div>
						</div>
						{navLinks.map(link => (
							<Link
								key={link.path}
								to={link.path}
								onClick={() => setMobileMenuOpen(false)}
								className={`block px-3 py-2 rounded-lg text-sm font-medium ${
									isActive(link.path)
										? 'bg-primary-50 text-primary-700'
										: 'text-gray-600 hover:bg-gray-50'
								}`}
							>
								{link.label}
							</Link>
						))}
						{user?.role === 'engineer' && (
							<Link
								to="/cart"
								onClick={() => setMobileMenuOpen(false)}
								className={`block px-3 py-2 rounded-lg text-sm font-medium ${
									isActive('/cart')
										? 'bg-primary-50 text-primary-700'
										: 'text-gray-600 hover:bg-gray-50'
								}`}
							>
								Cart {cartCount > 0 ? `(${cartCount})` : ''}
							</Link>
						)}
						<div className="pt-2 border-t border-gray-100">
							<button
								onClick={handleLogout}
								className="w-full text-left px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50"
							>
								Logout
							</button>
						</div>
					</div>
				</div>
			)}
		</nav>
	)
}
