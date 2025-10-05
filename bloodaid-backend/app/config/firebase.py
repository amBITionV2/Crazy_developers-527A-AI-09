import firebase_admin
from firebase_admin import credentials, auth, messaging
from app.config.settings import settings
import json
from typing import Optional

class FirebaseService:
    def __init__(self):
        self.app = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Load credentials
                if settings.FIREBASE_CREDENTIALS_PATH:
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                else:
                    # Use default credentials if available
                    cred = credentials.ApplicationDefault()
                
                self.app = firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized successfully")
            else:
                self.app = firebase_admin.get_app()
                print("✅ Firebase already initialized")
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            self.app = None
    
    def verify_id_token(self, id_token: str) -> Optional[dict]:
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None
    
    def create_custom_token(self, uid: str, additional_claims: dict = None) -> str:
        """Create custom token for user"""
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            return custom_token.decode('utf-8')
        except Exception as e:
            print(f"Custom token creation failed: {e}")
            return None
    
    def send_push_notification(self, token: str, title: str, body: str, data: dict = None):
        """Send push notification to device"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            
            response = messaging.send(message)
            print(f"Successfully sent message: {response}")
            return response
        except Exception as e:
            print(f"Push notification failed: {e}")
            return None
    
    def send_multicast_notification(self, tokens: list, title: str, body: str, data: dict = None):
        """Send notification to multiple devices"""
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            print(f"Successfully sent to {response.success_count} devices")
            return response
        except Exception as e:
            print(f"Multicast notification failed: {e}")
            return None

# Global Firebase service instance
firebase_service = FirebaseService()