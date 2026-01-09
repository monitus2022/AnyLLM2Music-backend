from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.progress import progress_emitter
from ..logger import app_logger

router = APIRouter()


@router.websocket("/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    await websocket.accept()
    app_logger.info(f"WebSocket connection accepted for session {session_id}")

    # Add connection to emitter
    progress_emitter.add_connection(session_id, websocket)

    try:
        while True:
            # Keep connection alive, wait for client messages if needed
            data = await websocket.receive_text()
            # For now, we don't expect client messages, but could handle pings or something
    except WebSocketDisconnect:
        app_logger.info(f"WebSocket disconnected for session {session_id}")
    finally:
        progress_emitter.remove_connection(session_id, websocket)