from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, WebSocketException, status

from backend.app.auth import verify_token


router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    try:
        verify_token(token)
    except Exception as exc:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from exc

    manager = websocket.app.state.ws_manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
