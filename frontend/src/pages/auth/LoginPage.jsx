import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { isValidEmail } from '../../utils/validators'

export default function LoginPage() {
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [loading, setLoading] = useState(false)
	const [errors, setErrors] = useState({})

	const { login } = useAuth()
	const navigate = useNavigate()

	const validate = () => {
		const errs = {}
		if (!email) errs.email = 'Email is required'
		else if (!isValidEmail(email)) errs.email = 'Invalid email format'
		if (!password) errs.password = 'Password is required'
		else if (password.length < 6) errs.password = 'Minimum 6 characters'
		setErrors(errs)
		return Object.keys(errs).length === 0
	}

	const handleSubmit = async (e) => {
		e.preventDefault()
		if (!validate()) return

		setLoading(true)
		try {
			const data = await login(email, password)

			// Redirect based on role
			const redirects = {
				engineer: '/menu',
				kitchen: '/kitchen',
				runner: '/runner',
				admin: '/admin',
			}
			navigate(redirects[data.role] || '/')
		} catch (error) {
			// Error handled in AuthContext
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-700 to-primary-900 px-3 sm:px-4 py-4">
			<div className="bg-white rounded-2xl shadow-2xl p-5 sm:p-8 w-full max-w-md animate-fade-in">
				{/* Logo */}
				<div className="text-center mb-8">
					<div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
						<span className="text-white font-bold text-2xl">PS</span>
					</div>
					<h1 className="text-xl sm:text-2xl font-bold text-gray-900">ProSensia Smart-Serve</h1>
					<p className="text-gray-500 mt-1">Sign in to your account</p>
				</div>

				{/* Form */}
				<form onSubmit={handleSubmit} className="space-y-5">
					{/* Email */}
					<div>
						<label className="input-label">Email</label>
						<input
							type="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							placeholder="engineer1@prosensia.com"
							className={`input-field ${errors.email ? 'input-error' : ''}`}
							disabled={loading}
						/>
						{errors.email && (
							<p className="text-accent-red text-xs mt-1">{errors.email}</p>
						)}
					</div>

					{/* Password */}
					<div>
						<label className="input-label">Password</label>
						<input
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							placeholder="••••••••"
							className={`input-field ${errors.password ? 'input-error' : ''}`}
							disabled={loading}
						/>
						{errors.password && (
							<p className="text-accent-red text-xs mt-1">{errors.password}</p>
						)}
					</div>

					{/* Submit */}
					<button
						type="submit"
						disabled={loading}
						className="btn-primary w-full btn-lg flex items-center justify-center"
					>
						{loading ? (
							<div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
						) : (
							'Sign In'
						)}
					</button>
				</form>

				{/* Demo Accounts */}
				<div className="mt-6 p-4 bg-gray-50 rounded-xl">
					<p className="text-xs font-semibold text-gray-500 mb-2">DEMO ACCOUNTS</p>
					<div className="space-y-1 text-xs text-gray-600">
						<p><span className="font-medium">Engineer:</span> engineer1@prosensia.com / engineer123</p>
						<p><span className="font-medium">Kitchen:</span> kitchen1@prosensia.com / kitchen123</p>
						<p><span className="font-medium">Runner:</span> runner1@prosensia.com / runner123</p>
						<p><span className="font-medium">Admin:</span> admin@prosensia.com / admin123</p>
					</div>
				</div>
			</div>
		</div>
	)
}
