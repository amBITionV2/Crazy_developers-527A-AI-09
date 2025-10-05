from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept websocket connection and add to active connections"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        print(f"✅ WebSocket connected for user: {user_id}")
    
    def disconnect(self, user_id: str, websocket: WebSocket = None):
        """Remove websocket connection"""
        if user_id in self.active_connections:
            if websocket:
                try:
                    self.active_connections[user_id].remove(websocket)
                except ValueError:
                    pass
            
            # Clean up empty connection lists
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        print(f"❌ WebSocket disconnected for user: {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected_sockets = []
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    disconnected_sockets.append(websocket)
            
            # Clean up disconnected sockets
            for socket in disconnected_sockets:
                self.disconnect(user_id, socket)
    
    async def broadcast(self, message: dict, user_ids: List[str] = None):
        """Broadcast message to multiple users or all connected users"""
        if user_ids is None:
            user_ids = list(self.active_connections.keys())
        
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    async def send_emergency_alert(self, alert_data: dict, nearby_donor_ids: List[str]):
        """Send emergency alert to nearby donors"""
        message = {
            "type": "emergency_alert",
            "data": alert_data,
            "timestamp": alert_data.get("created_at")
        }
        
        await self.broadcast(message, nearby_donor_ids)
        print(f"🚨 Emergency alert sent to {len(nearby_donor_ids)} donors")
    
    async def send_donation_request(self, request_data: dict, donor_id: str):
        """Send donation request to specific donor"""
        message = {
            "type": "donation_request",
            "data": request_data,
            "timestamp": request_data.get("created_at")
        }
        
        await self.send_personal_message(message, donor_id)
        print(f"💌 Donation request sent to donor: {donor_id}")
    
    async def send_response_notification(self, response_data: dict, patient_id: str):
        """Send donor response notification to patient"""
        message = {
            "type": "donor_response",
            "data": response_data,
            "timestamp": response_data.get("created_at")
        }
        
        await self.send_personal_message(message, patient_id)
        print(f"📬 Response notification sent to patient: {patient_id}")
    
    def get_connected_users(self) -> List[str]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if user is currently connected"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0