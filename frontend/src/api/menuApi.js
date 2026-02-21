import api from './axiosInstance'

const menuApi = {
	getMenu: async () => {
		const response = await api.get('/menu')
		return response.data
	},

	getFullMenu: async () => {
		const response = await api.get('/menu/all')
		return response.data
	},
}

export default menuApi
