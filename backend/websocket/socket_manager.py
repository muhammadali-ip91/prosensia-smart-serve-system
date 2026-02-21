"""Socket.IO Server Setup"""

import socketio
from loguru import logger
from fastapi import FastAPI
from config import settings


def _create_client_manager():
    """Create Redis client manager when horizontal scaling is enabled."""
    if not settings.SOCKETIO_USE_REDIS_MANAGER:
        return None

    try:
        manager = socketio.AsyncRedisManager(
            settings.REDIS_URL,
            channel=settings.SOCKETIO_REDIS_CHANNEL,
        )
        logger.info(
            "Socket.IO Redis manager enabled "
            f"(channel={settings.SOCKETIO_REDIS_CHANNEL})"
        )
        return manager
    except Exception as exc:
        logger.warning(
            "Failed to initialize Socket.IO Redis manager, "
            f"falling back to single-instance mode: {exc}"
        )
        return None


# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    client_manager=_create_client_manager(),
    cors_allowed_origins=settings.cors_origins_list or "*",
    logger=False,
    ping_interval=settings.SOCKETIO_PING_INTERVAL,
    ping_timeout=settings.SOCKETIO_PING_TIMEOUT,
    max_http_buffer_size=settings.SOCKETIO_MAX_HTTP_BUFFER_SIZE,
)


def create_socket_app(app: FastAPI):
    """Wrap FastAPI app with Socket.IO"""

    socket_app = socketio.ASGIApp(sio, app)

    # Register event handlers
    register_events()

    return socket_app


def register_events():
    """Register Socket.IO event handlers"""

    @sio.event
    async def connect(sid, environ):
        logger.info(f"WebSocket connected: {sid}")

    @sio.event
    async def disconnect(sid):
        logger.info(f"WebSocket disconnected: {sid}")

    @sio.event
    async def join_room(sid, data):
        """Client joins a room for targeted updates"""
        room = data.get("room")
        if room:
            await sio.enter_room(sid, room)
            logger.info(f"Client {sid} joined room: {room}")

    @sio.event
    async def leave_room(sid, data):
        """Client leaves a room"""
        room = data.get("room")
        if room:
            await sio.leave_room(sid, room)
            logger.info(f"Client {sid} left room: {room}")


async def emit_order_update(order_id: str, engineer_id: str, data: dict):
    """Emit order status update to engineer"""
    room = f"engineer_{engineer_id}"
    await sio.emit("order_status_update", data, room=room)
    logger.info(f"Order update sent to {room}: {data.get('new_status')}")


async def emit_order_update_to_runner(runner_id: str, data: dict):
    """Emit order status update to assigned runner"""
    room = f"runner_{runner_id}"
    await sio.emit("order_status_update", data, room=room)
    logger.info(f"Order update sent to {room}: {data.get('new_status')}")


async def emit_order_update_to_kitchen(data: dict):
    """Emit order status update to kitchen dashboard"""
    await sio.emit("order_status_update", data, room="kitchen")
    logger.info(f"Order update sent to kitchen: {data.get('new_status')}")


async def emit_new_order_to_kitchen(data: dict):
    """Emit new order notification to kitchen"""
    await sio.emit("new_order", data, room="kitchen")
    logger.info(f"New order sent to kitchen: {data.get('order_id')}")


async def emit_new_delivery_to_runner(runner_id: str, data: dict):
    """Emit new delivery assignment to runner"""
    room = f"runner_{runner_id}"
    await sio.emit("new_delivery", data, room=room)
    logger.info(f"Delivery assigned to {room}: {data.get('order_id')}")


async def emit_eta_update(engineer_id: str, data: dict):
    """Emit ETA update to engineer"""
    room = f"engineer_{engineer_id}"
    await sio.emit("eta_update", data, room=room)
