import { createContext, useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import { useAuth } from '../hooks/useAuth'

export const SocketContext = createContext(null)

const resolveSocketHost = () => {
	if (typeof window === 'undefined') return 'localhost'

	const host = window.location.hostname
	if (!host || host === '0.0.0.0' || host === '::' || host === '[::]') {
		return 'localhost'
	}

	return host
}

const defaultSocketUrl = typeof window !== 'undefined'
	? `${window.location.protocol}//${resolveSocketHost()}:8000`
	: 'http://localhost:8000'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || defaultSocketUrl

export function SocketProvider({ children }) {
	const [isConnected, setIsConnected] = useState(false)
	const socketRef = useRef(null)
	const { user } = useAuth()

	useEffect(() => {
		if (!user) {
			// Disconnect if user logs out
			if (socketRef.current) {
				socketRef.current.disconnect()
				socketRef.current = null
				setIsConnected(false)
			}
			return
		}

		// Create connection
		const socket = io(SOCKET_URL, {
			transports: ['websocket', 'polling'],
			reconnection: true,
			reconnectionAttempts: 10,
			reconnectionDelay: 1000,
			reconnectionDelayMax: 30000,
		})

		socketRef.current = socket

		// Connection events
		socket.on('connect', () => {
			setIsConnected(true)
			console.log('🟢 WebSocket connected')

			// Join user-specific room
			if (user.role === 'engineer') {
				socket.emit('join_room', { room: `engineer_${user.user_id}` })
			} else if (user.role === 'runner') {
				socket.emit('join_room', { room: `runner_${user.user_id}` })
			} else if (user.role === 'kitchen') {
				socket.emit('join_room', { room: 'kitchen' })
			} else if (user.role === 'admin') {
				socket.emit('join_room', { room: 'admin' })
			}
		})

		socket.on('disconnect', () => {
			setIsConnected(false)
			console.log('🔴 WebSocket disconnected')
		})

		socket.on('connect_error', (error) => {
			console.log('⚠️ WebSocket error:', error.message)
		})

		// Cleanup on unmount
		return () => {
			socket.disconnect()
			socketRef.current = null
		}
	}, [user])

	const value = {
		socket: socketRef.current,
		isConnected,
	}

	return (
		<SocketContext.Provider value={value}>
			{children}
		</SocketContext.Provider>
	)
}
