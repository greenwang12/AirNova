# backend/routes/realtime.py
from fastapi import APIRouter, WebSocket, Query
from ..utils.ws_manager import WSManager

router = APIRouter(prefix="/realtime", tags=["realtime"])

# single manager instance used by app
ws_mgr = WSManager()

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, customer_id: int = Query(..., description="Customer ID for this websocket")):
    """
    Connect with: ws://HOST/realtime/ws?customer_id=1
    Note: this is a demo auth-free connection. For production, authenticate (JWT).
    """
    await ws_mgr.connect(customer_id, ws)
    try:
        while True:
            # keep connection alive; optionally receive pings from client
            msg = await ws.receive_text()
            # echo ping/pong or ignore
            if msg.lower() == "ping":
                await ws.send_text('{"type":"pong"}')
    except Exception:
        # disconnect on any error / client close
        ws_mgr.disconnect(customer_id, ws)
