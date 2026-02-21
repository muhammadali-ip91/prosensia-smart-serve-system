/** @type {import('tailwindcss').Config} */
export default {
	content: [
		"./index.html",
		"./src/**/*.{js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			colors: {
				primary: {
					50: '#EBF5FB',
					100: '#D6EAF8',
					200: '#AED6F1',
					300: '#85C1E9',
					400: '#5DADE2',
					500: '#2E86C1',
					600: '#2471A3',
					700: '#1A5276',
					800: '#154360',
					900: '#0E2F44',
				},
				accent: {
					green: '#27AE60',
					orange: '#E67E22',
					red: '#E74C3C',
					yellow: '#F39C12',
				},
				status: {
					placed: '#3498DB',
					confirmed: '#2980B9',
					preparing: '#E67E22',
					ready: '#27AE60',
					pickedup: '#16A085',
					ontheway: '#8E44AD',
					delivered: '#27AE60',
					cancelled: '#E74C3C',
					rejected: '#C0392B',
					delayed: '#F39C12',
				}
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', 'sans-serif'],
			},
			animation: {
				'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
				'slide-in': 'slideIn 0.3s ease-out',
				'fade-in': 'fadeIn 0.3s ease-out',
			},
			keyframes: {
				slideIn: {
					'0%': { transform: 'translateY(-10px)', opacity: '0' },
					'100%': { transform: 'translateY(0)', opacity: '1' },
				},
				fadeIn: {
					'0%': { opacity: '0' },
					'100%': { opacity: '1' },
				},
			}
		},
	},
	plugins: [],
}
