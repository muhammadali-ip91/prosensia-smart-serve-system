import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

// Context Providers
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import { SocketProvider } from './context/SocketContext'
import { NotificationProvider } from './context/NotificationContext'

ReactDOM.createRoot(document.getElementById('root')).render(
	<React.StrictMode>
		<BrowserRouter>
			<AuthProvider>
				<SocketProvider>
					<NotificationProvider>
						<CartProvider>
							<App />
						</CartProvider>
					</NotificationProvider>
				</SocketProvider>
			</AuthProvider>
		</BrowserRouter>
	</React.StrictMode>
)
