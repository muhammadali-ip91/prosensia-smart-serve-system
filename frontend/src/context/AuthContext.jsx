import { createContext, useState, useEffect } from 'react'
import authApi from '../api/authApi'
import toast from 'react-hot-toast'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
	const [user, setUser] = useState(null)
	const [loading, setLoading] = useState(true)

	// Check for existing session on mount
	useEffect(() => {
		const checkAuth = async () => {
			const token = localStorage.getItem('access_token')
			const savedUser = localStorage.getItem('user')

			if (token && savedUser) {
				try {
					setUser(JSON.parse(savedUser))
					// Verify token is still valid
					const userData = await authApi.getMe()
					setUser(userData)
					localStorage.setItem('user', JSON.stringify(userData))
				} catch (error) {
					// Token expired or invalid
					localStorage.removeItem('access_token')
					localStorage.removeItem('refresh_token')
					localStorage.removeItem('user')
					setUser(null)
				}
			}
			setLoading(false)
		}

		checkAuth()
	}, [])

	const login = async (email, password) => {
		try {
			const data = await authApi.login(email, password)

			// Save tokens
			localStorage.setItem('access_token', data.access_token)
			localStorage.setItem('refresh_token', data.refresh_token)
			localStorage.setItem('user', JSON.stringify(data.user))

			setUser(data.user)
			toast.success(`Welcome, ${data.user.name}!`)

			return data
		} catch (error) {
			const message = error.response?.data?.error?.message || 'Login failed'
			toast.error(message)
			throw error
		}
	}

	const logout = async () => {
		try {
			await authApi.logout()
		} catch (error) {
			// Proceed with local logout even if server logout fails
		}

		localStorage.removeItem('access_token')
		localStorage.removeItem('refresh_token')
		localStorage.removeItem('user')
		setUser(null)
		toast.success('Logged out successfully')
	}

	const value = {
		user,
		loading,
		login,
		logout,
		isAuthenticated: !!user,
		isEngineer: user?.role === 'engineer',
		isKitchen: user?.role === 'kitchen',
		isRunner: user?.role === 'runner',
		isAdmin: user?.role === 'admin',
	}

	return (
		<AuthContext.Provider value={value}>
			{children}
		</AuthContext.Provider>
	)
}
