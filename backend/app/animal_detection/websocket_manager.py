"""
WebSocket Connection Manager for real-time IoT Animal Detection broadcasts.
Thread-safe and async-safe with automatic stale connection pruning.
"""
import asyncio
from typing import List, Dict, Any
from fastapi import WebSocket
import structlog

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts real-time detection events."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accepts a new WebSocket connection and adds it to the active list."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info("iot_websocket_connected", total_connections=len(self.active_connections))

    async def disconnect(self, websocket: WebSocket):
        """Removes a WebSocket from the active list."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info("iot_websocket_disconnected", total_connections=len(self.active_connections))

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a JSON-serializable message to all active WebSocket clients concurrently."""
        async with self._lock:
            connections = list(self.active_connections)

        if not connections:
            return

        stale_connections = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning("iot_websocket_send_failed", error=str(e))
                stale_connections.append(connection)

        if stale_connections:
            async with self._lock:
                for stale in stale_connections:
                    if stale in self.active_connections:
                        self.active_connections.remove(stale)


# Global singleton instance
manager = ConnectionManager()
