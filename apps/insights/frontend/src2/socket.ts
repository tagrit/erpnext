import { io, Socket } from 'socket.io-client'
import { socketio_port } from '../../../../sites/common_site_config.json'

let socket: Socket

export function getSocket() {
	if (socket) {
		return socket
	}

	let host = window.location.hostname
	let siteName = import.meta.env.DEV ? host : window.site_name
	let port = window.location.port ? `:${socketio_port}` : ''
	let protocol = port ? 'http' : 'https'
	let url = `${protocol}://${host}${port}/${siteName}`

	socket = io(url, {
		withCredentials: true,
		reconnectionAttempts: 5,
	})
	return socket
}
