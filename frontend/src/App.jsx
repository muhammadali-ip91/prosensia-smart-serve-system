import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuth } from './hooks/useAuth'

// Layouts
import Navbar from './components/common/Navbar'
import Footer from './components/common/Footer'
import OfflineBanner from './components/common/OfflineBanner'
import ProtectedRoute from './components/common/ProtectedRoute'

// Auth Pages
import LoginPage from './pages/auth/LoginPage'

// Engineer Pages
import MenuPage from './pages/engineer/MenuPage'
import CartPage from './pages/engineer/CartPage'
import OrderConfirmationPage from './pages/engineer/OrderConfirmationPage'
import OrderTrackingPage from './pages/engineer/OrderTrackingPage'
import OrderHistoryPage from './pages/engineer/OrderHistoryPage'
import FeedbackPage from './pages/engineer/FeedbackPage'
import ProfilePage from './pages/engineer/ProfilePage'

// Kitchen Pages
import KitchenDashboardPage from './pages/kitchen/KitchenDashboardPage'

// Runner Pages
import RunnerDashboardPage from './pages/runner/RunnerDashboardPage'

// Admin Pages
import AdminDashboardPage from './pages/admin/AdminDashboardPage'
import MenuManagementPage from './pages/admin/MenuManagementPage'
import UserManagementPage from './pages/admin/UserManagementPage'

// Trivia Pages
import TriviaGamePage from './pages/trivia/TriviaGamePage'
import LeaderboardPage from './pages/trivia/LeaderboardPage'

// Common Pages
import NotFoundPage from './pages/common/NotFoundPage'

function App() {
	const { user, loading } = useAuth()
	const location = useLocation()
	const isAuthPage = location.pathname === '/login'
	const [isMobile, setIsMobile] = useState(false)

	useEffect(() => {
		const mediaQuery = window.matchMedia('(max-width: 640px)')
		const updateView = () => setIsMobile(mediaQuery.matches)
		updateView()

		if (mediaQuery.addEventListener) {
			mediaQuery.addEventListener('change', updateView)
			return () => mediaQuery.removeEventListener('change', updateView)
		}

		mediaQuery.addListener(updateView)
		return () => mediaQuery.removeListener(updateView)
	}, [])

	if (loading) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50">
				<div className="text-center">
					<div className="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
					<p className="text-gray-600 text-lg">Loading ProSensia Smart-Serve...</p>
				</div>
			</div>
		)
	}

	return (
		<div className="min-h-screen flex flex-col bg-gray-50">
			{/* Offline Banner */}
			<OfflineBanner />

			{/* Toast Notifications */}
			<Toaster
				position={isMobile ? 'top-center' : 'top-right'}
				containerStyle={
					isMobile
						? { top: 76, left: 10, right: 10, bottom: 'unset' }
						: undefined
				}
				gutter={8}
				toastOptions={{
					duration: isMobile ? 2600 : 3500,
					style: {
						background: '#fff',
						color: '#1f2937',
						boxShadow: '0 8px 24px rgba(15, 23, 42, 0.16)',
						borderRadius: isMobile ? '14px' : '12px',
						padding: isMobile ? '12px 14px' : '14px 16px',
						maxWidth: isMobile ? 'calc(100vw - 20px)' : '420px',
						width: isMobile ? '100%' : 'auto',
					},
					success: {
						iconTheme: { primary: '#27AE60', secondary: '#fff' }
					},
					error: {
						iconTheme: { primary: '#E74C3C', secondary: '#fff' }
					}
				}}
			/>

			{/* Navbar (hidden on auth pages) */}
			{user && !isAuthPage && <Navbar />}

			{/* Main Content */}
			<main className="flex-1">
				<Routes>
					{/* ======== PUBLIC ROUTES ======== */}
					<Route
						path="/login"
						element={<LoginPage />}
					/>

					{/* ======== ENGINEER ROUTES ======== */}
					<Route path="/" element={<Navigate to="/login" replace />} />
					<Route path="/menu" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<MenuPage />
						</ProtectedRoute>
					} />
					<Route path="/cart" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<CartPage />
						</ProtectedRoute>
					} />
					<Route path="/order/confirmation/:orderId" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<OrderConfirmationPage />
						</ProtectedRoute>
					} />
					<Route path="/order/track/:orderId" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<OrderTrackingPage />
						</ProtectedRoute>
					} />
					<Route path="/orders" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<OrderHistoryPage />
						</ProtectedRoute>
					} />
					<Route path="/feedback/:orderId" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<FeedbackPage />
						</ProtectedRoute>
					} />
					<Route path="/profile" element={
						<ProtectedRoute allowedRoles={['engineer', 'kitchen', 'runner', 'admin']}>
							<ProfilePage />
						</ProtectedRoute>
					} />

					{/* ======== TRIVIA ROUTES ======== */}
					<Route path="/trivia" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<TriviaGamePage />
						</ProtectedRoute>
					} />
					<Route path="/trivia/leaderboard" element={
						<ProtectedRoute allowedRoles={['engineer']}>
							<LeaderboardPage />
						</ProtectedRoute>
					} />

					{/* ======== KITCHEN ROUTES ======== */}
					<Route path="/kitchen" element={
						<ProtectedRoute allowedRoles={['kitchen', 'admin']}>
							<KitchenDashboardPage />
						</ProtectedRoute>
					} />

					{/* ======== RUNNER ROUTES ======== */}
					<Route path="/runner" element={
						<ProtectedRoute allowedRoles={['runner', 'admin']}>
							<RunnerDashboardPage />
						</ProtectedRoute>
					} />

					{/* ======== ADMIN ROUTES ======== */}
					<Route path="/admin" element={
						<ProtectedRoute allowedRoles={['admin']}>
							<AdminDashboardPage />
						</ProtectedRoute>
					} />
					<Route path="/admin/menu" element={
						<ProtectedRoute allowedRoles={['admin']}>
							<MenuManagementPage />
						</ProtectedRoute>
					} />
					<Route path="/admin/users" element={
						<ProtectedRoute allowedRoles={['admin']}>
							<UserManagementPage />
						</ProtectedRoute>
					} />

					{/* ======== 404 ======== */}
					<Route path="*" element={<NotFoundPage />} />
				</Routes>
			</main>

			{/* Footer */}
			{user && !isAuthPage && <Footer />}
		</div>
	)
}

export default App
