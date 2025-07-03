# app/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.deps import get_db
from typing import Dict, Set
import json
import asyncio

# Create router instance - THIS WAS MISSING!
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, agent_id: str):
        await websocket.accept()
        if agent_id not in self.active_connections:
            self.active_connections[agent_id] = set()
        self.active_connections[agent_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, agent_id: str):
        if agent_id in self.active_connections:
            self.active_connections[agent_id].discard(websocket)
            if not self.active_connections[agent_id]:
                del self.active_connections[agent_id]
    
    async def send_agent_update(self, agent_id: str, data: dict):
        if agent_id in self.active_connections:
            for connection in self.active_connections[agent_id]:
                try:
                    await connection.send_json(data)
                except:
                    pass

manager = ConnectionManager()

@router.websocket("/ws/agents/{agent_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: str
):
    await manager.connect(websocket, agent_id)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, agent_id)
