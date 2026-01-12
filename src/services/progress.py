import json
from typing import Dict, List
from fastapi import WebSocket
from ..logger import app_logger


class ProgressEmitter:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    def add_connection(self, session_id: str, websocket: WebSocket):
        if session_id not in self.connections:
            self.connections[session_id] = []
        self.connections[session_id].append(websocket)
        app_logger.info(f"WebSocket connection added for session {session_id}")

    def remove_connection(self, session_id: str, websocket: WebSocket):
        if session_id in self.connections:
            try:
                self.connections[session_id].remove(websocket)
                if not self.connections[session_id]:
                    del self.connections[session_id]
                app_logger.info(f"WebSocket connection removed for session {session_id}")
            except ValueError:
                pass  # WebSocket not in list

    async def emit_progress(self, session_id: str, stage: str, message: str, percentage: int = None):
        data = {"type": "progress", "stage": stage, "message": message}
        if percentage is not None:
            data["percentage"] = percentage
        await self._emit(session_id, data)

    async def emit_error(self, session_id: str, stage: str, message: str):
        await self._emit(session_id, {"type": "error", "stage": stage, "message": message})

    async def emit_complete(self, session_id: str, stage: str = "all", message: str = "Completed successfully"):
        await self._emit(session_id, {"type": "complete", "stage": stage, "message": message})

    async def _emit(self, session_id: str, data: dict):
        if session_id not in self.connections:
            return
        message = json.dumps(data)
        disconnected = []
        for ws in self.connections[session_id]:
            try:
                await ws.send_text(message)
            except Exception as e:
                app_logger.warning(f"Failed to send message to WebSocket for session {session_id}: {e}")
                disconnected.append(ws)
        # Remove disconnected websockets
        for ws in disconnected:
            self.remove_connection(session_id, ws)


progress_emitter = ProgressEmitter()