import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import triviaApi from '../../api/triviaApi'
import LoadingSpinner from '../../components/common/LoadingSpinner'

export default function LeaderboardPage() {
	const [leaderboard, setLeaderboard] = useState([])
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		fetchLeaderboard()
	}, [])

	const fetchLeaderboard = async () => {
		try {
			const data = await triviaApi.getLeaderboard(10)
			setLeaderboard(data.leaderboard || [])
		} catch (error) { console.error(error) }
		finally { setLoading(false) }
	}

	if (loading) return <LoadingSpinner size="lg" />

	const medals = ['🥇', '🥈', '🥉']

	return (
		<div className="page-container max-w-2xl mx-auto">
			<div className="flex items-center justify-between mb-6">
				<h1 className="page-title mb-0">🏆 Leaderboard</h1>
				<Link to="/trivia" className="btn-primary btn-sm">Play Trivia</Link>
			</div>

			<p className="text-gray-500 mb-6">Weekly rankings • Resets every Monday</p>

			<div className="card">
				{leaderboard.length === 0 ? (
					<p className="text-center text-gray-400 py-8">No scores yet this week</p>
				) : (
					<div className="space-y-3">
						{leaderboard.map((entry, index) => (
							<div key={entry.engineer_id} className={`flex items-center space-x-4 p-3 rounded-xl ${index < 3 ? 'bg-yellow-50' : 'hover:bg-gray-50'}`}>
								<span className="text-2xl w-10 text-center">
									{index < 3 ? medals[index] : `#${entry.rank}`}
								</span>
								<div className="flex-1">
									<p className="font-bold text-gray-900">{entry.engineer_name}</p>
									<p className="text-xs text-gray-500">
										{entry.questions_answered} questions • {entry.accuracy}% accuracy
									</p>
								</div>
								<span className="text-xl font-bold text-primary-700">{entry.total_points}</span>
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	)
}
