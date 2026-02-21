import { useSocket } from '../../hooks/useSocket'

export default function ConnectionIndicator() {
	const { isConnected } = useSocket()

	return (
		<div className="flex items-center space-x-1.5" title={isConnected ? 'Connected' : 'Disconnected'}>
			<div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`}></div>
			<span className="text-xs text-gray-500 hidden sm:block">
				{isConnected ? 'Live' : 'Offline'}
			</span>
		</div>
	)
}
