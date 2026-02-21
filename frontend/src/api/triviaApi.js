import api from './axiosInstance'

const triviaApi = {
	getQuestion: async () => {
		const response = await api.get('/trivia/question')
		return response.data
	},

	submitAnswer: async (questionId, selectedOption, timeTaken) => {
		const response = await api.post('/trivia/answer', {
			question_id: questionId,
			selected_option: selectedOption,
			time_taken_seconds: timeTaken
		})
		return response.data
	},

	getLeaderboard: async (limit = 10) => {
		const response = await api.get(`/trivia/leaderboard?limit=${limit}`)
		return response.data
	},
}

export default triviaApi
