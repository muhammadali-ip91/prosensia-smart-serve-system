import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import triviaApi from '../../api/triviaApi'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import toast from 'react-hot-toast'

export default function TriviaGamePage() {
	const [question, setQuestion] = useState(null)
	const [loading, setLoading] = useState(true)
	const [selected, setSelected] = useState(null)
	const [result, setResult] = useState(null)
	const [timer, setTimer] = useState(15)
	const [submitting, setSubmitting] = useState(false)
	const timerRef = useRef(null)
	const startTimeRef = useRef(null)

	useEffect(() => { loadQuestion() }, [])

	useEffect(() => {
		if (question && !result) {
			startTimeRef.current = Date.now()
			setTimer(15)
			timerRef.current = setInterval(() => {
				setTimer(prev => {
					if (prev <= 1) {
						clearInterval(timerRef.current)
						handleTimeUp()
						return 0
					}
					return prev - 1
				})
			}, 1000)
		}
		return () => clearInterval(timerRef.current)
	}, [question, result])

	const loadQuestion = async () => {
		setLoading(true)
		setSelected(null)
		setResult(null)
		try {
			const data = await triviaApi.getQuestion()
			setQuestion(data)
		} catch (error) {
			console.error(error)
		} finally {
			setLoading(false)
		}
	}

	const handleTimeUp = () => {
		toast.error("Time's up! ⏰")
		setResult({ correct: false, correct_option: question?.correct_option || '?', points_earned: 0, total_score: 0 })
	}

	const handleAnswer = async (option) => {
		if (result || submitting) return
		clearInterval(timerRef.current)

		setSelected(option)
		setSubmitting(true)

		const timeTaken = Math.round((Date.now() - startTimeRef.current) / 1000)

		try {
			const data = await triviaApi.submitAnswer(question.question_id, option, timeTaken)
			setResult(data)
			if (data.correct) toast.success(`Correct! +${data.points_earned} points 🎉`)
			else toast.error('Wrong answer 😅')
		} catch (error) {
			console.error(error)
		} finally {
			setSubmitting(false)
		}
	}

	if (loading) return <LoadingSpinner size="lg" text="Loading question..." />

	if (!question) {
		return (
			<div className="page-container text-center py-16">
				<div className="text-6xl mb-4">🎮</div>
				<h2 className="text-xl font-bold mb-2">No questions available</h2>
				<Link to="/menu" className="btn-primary mt-4">Back to Menu</Link>
			</div>
		)
	}

	const options = [
		{ key: 'A', text: question.option_a },
		{ key: 'B', text: question.option_b },
		{ key: 'C', text: question.option_c },
		{ key: 'D', text: question.option_d },
	]

	return (
		<div className="page-container max-w-2xl mx-auto">
			<div className="flex items-center justify-between mb-6">
				<h1 className="text-2xl font-bold">🧠 Tech Trivia</h1>
				<Link to="/trivia/leaderboard" className="btn-outline btn-sm">🏆 Leaderboard</Link>
			</div>

			<div className="card">
				{/* Timer */}
				<div className="flex items-center justify-between mb-6">
					<span className="text-sm text-gray-500">
						{question.category} • {question.difficulty}
					</span>
					<div className={`text-2xl font-bold ${timer <= 5 ? 'text-red-600 animate-pulse' : 'text-primary-600'}`}>
						⏱️ {timer}s
					</div>
				</div>

				{/* Timer Bar */}
				<div className="w-full bg-gray-200 rounded-full h-2 mb-6">
					<div
						className={`h-2 rounded-full transition-all duration-1000 ${timer <= 5 ? 'bg-red-500' : 'bg-primary-500'}`}
						style={{ width: `${(timer / 15) * 100}%` }}
					></div>
				</div>

				{/* Question */}
				<h2 className="text-xl font-bold text-gray-900 mb-6">{question.question_text}</h2>

				{/* Options */}
				<div className="space-y-3">
					{options.map(opt => {
						let bgClass = 'bg-gray-50 hover:bg-primary-50 border-gray-200 hover:border-primary-300 cursor-pointer'

						if (result) {
							if (opt.key === result.correct_option) {
								bgClass = 'bg-green-50 border-green-500 text-green-800'
							} else if (opt.key === selected && !result.correct) {
								bgClass = 'bg-red-50 border-red-500 text-red-800'
							} else {
								bgClass = 'bg-gray-50 border-gray-200 opacity-50'
							}
						} else if (selected === opt.key) {
							bgClass = 'bg-primary-50 border-primary-500'
						}

						return (
							<button
								key={opt.key}
								onClick={() => handleAnswer(opt.key)}
								disabled={!!result}
								className={`w-full text-left p-4 rounded-xl border-2 transition-all ${bgClass}`}
							>
								<span className="font-bold mr-3">{opt.key}.</span>
								{opt.text}
							</button>
						)
					})}
				</div>

				{/* Result */}
				{result && (
					<div className="mt-6 text-center animate-fade-in">
						<p className="text-lg font-bold mb-2">
							{result.correct ? '🎉 Correct!' : `❌ Wrong! Answer: ${result.correct_option}`}
						</p>
						<p className="text-sm text-gray-500 mb-4">
							Points earned: {result.points_earned} | Total: {result.total_score}
						</p>
						<button onClick={loadQuestion} className="btn-primary">Next Question →</button>
					</div>
				)}
			</div>
		</div>
	)
}
