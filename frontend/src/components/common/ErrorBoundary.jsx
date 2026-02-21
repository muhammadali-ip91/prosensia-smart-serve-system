import { Component } from 'react'

export default class ErrorBoundary extends Component {
	constructor(props) {
		super(props)
		this.state = { hasError: false, error: null }
	}

	static getDerivedStateFromError(error) {
		return { hasError: true, error }
	}

	componentDidCatch(error, errorInfo) {
		console.error('ErrorBoundary caught:', error, errorInfo)
	}

	render() {
		if (this.state.hasError) {
			return (
				<div className="min-h-[60vh] flex items-center justify-center">
					<div className="text-center p-8">
						<div className="text-6xl mb-4">😵</div>
						<h2 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h2>
						<p className="text-gray-500 mb-6">An unexpected error occurred.</p>
						<button
							onClick={() => window.location.reload()}
							className="btn-primary"
						>
							Reload Page
						</button>
					</div>
				</div>
			)
		}

		return this.props.children
	}
}
