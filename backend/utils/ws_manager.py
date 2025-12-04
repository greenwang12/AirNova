# backend/utils/ws_manager.py
from typing import Dict, Set
from fastapi import WebSocket
import asyncio
import json

class WSManager:
    def __init__(self):
        # mapping: customer_id -> set of WebSocket
        self.clients: Dict[int, Set[WebSocket]] = {}

    async def connect(self, customer_id: int, ws: WebSocket):
        await ws.accept()
        conns = self.clients.setdefault(customer_id, set())
        conns.add(ws)

    def disconnect(self, customer_id: int, ws: WebSocket):
        conns = self.clients.get(customer_id)
        if not conns:
            return
        if ws in conns:
            conns.remove(ws)
        if not conns:
            # remove empty set
            self.clients.pop(customer_id, None)

    async def send(self, customer_id: int, data: dict):
        conns = list(self.clients.get(customer_id, set()))
        if not conns:
            return False
        payload = json.dumps(data)
        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception:
                # swallow/send cleanup; remove bad connection
                try:
                    self.disconnect(customer_id, ws)
                except Exception:
                    pass
        return True

    async def broadcast(self, data: dict):
        payload = json.dumps(data)
        for cid, conns in list(self.clients.items()):
            for ws in list(conns):
                try:
                    await ws.send_text(payload)
                except Exception:
                    self.disconnect(cid, ws)
