import { Link } from 'react-router-dom'

export default function NotFoundPage() {
	return (
		<div className="min-h-[70vh] flex items-center justify-center">
			<div className="text-center">
				<h1 className="text-8xl font-bold text-gray-200 mb-4">404</h1>
				<h2 className="text-2xl font-bold text-gray-900 mb-2">Page Not Found</h2>
				<p className="text-gray-500 mb-6">The page you are looking for does not exist.</p>
				<Link to="/" className="btn-primary">Go Home</Link>
			</div>
		</div>
	)
}
