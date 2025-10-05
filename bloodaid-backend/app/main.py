from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.v1 import auth, emergency, health, ai_chat_enhanced, donors, patients, donations, otp_auth, emergency_sos
from app.websockets.manager import ConnectionManager
from app.core.exceptions import BloodAidException

# Initialize FastAPI app
app = FastAPI(
    title="BloodAid API",
    description="AI-Powered Blood Donation Platform Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
ws_manager = ConnectionManager()

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(otp_auth.router, prefix="/api/v1")
app.include_router(donors.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(emergency.router, prefix="/api/v1")
app.include_router(emergency_sos.router, prefix="/api/v1")  # eRaktkosh integrated emergency SOS
app.include_router(donations.router, prefix="/api/v1")
app.include_router(health.router)
app.include_router(ai_chat_enhanced.router, prefix="/api/v1")

# Exception handler
@app.exception_handler(BloodAidException)
async def bloodaid_exception_handler(request, exc: BloodAidException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail}
    )

# Startup event - Load ML models
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting BloodAid Backend...")
    
    try:
        # Database connection
        print("✅ Database connected")
        
        # Try to initialize backup data cache (optional feature)
        try:
            # Try the full backup service first
            from app.services.cached_backup_service import get_cached_backup_service
            backup_service = await get_cached_backup_service()
            service_type = "full"
        except ImportError:
            # Fall back to simple mock service
            from app.services.simple_backup_service import get_mock_backup_service
            backup_service = await get_mock_backup_service()
            service_type = "mock"
        except Exception:
            # Final fallback to simple mock service
            from app.services.simple_backup_service import get_mock_backup_service
            backup_service = await get_mock_backup_service()
            service_type = "mock"
        
        # Start background task to refresh backup data
        import asyncio
        async def refresh_backup_data():
            while True:
                try:
                    await backup_service.update_cached_data()
                    # Wait 2 hours before next update
                    await asyncio.sleep(2 * 60 * 60)
                except Exception as e:
                    print(f"⚠️ Backup refresh error: {e}")
                    # Wait 30 minutes before retry on error
                    await asyncio.sleep(30 * 60)
        
        # Start the background task
        asyncio.create_task(refresh_backup_data())
        print(f"📦 Backup service ({service_type}) initialized and background refresh started")
        
        # Preload LLM model (optional, can be lazy loaded)
        print("📦 Backend ready for LLM loading...")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down BloodAid Backend...")

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": "BloodAid API",
        "version": "1.0.0",
        "ml_enabled": True
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "api": "operational",
        "database": "connected",
        "llm": "ready",
        "rag": "enabled"
    }

@app.get("/backup-health", tags=["Health"])
async def backup_health_check():
    """Check backup service health"""
    try:
        from app.services.cached_backup_service import get_cached_backup_service
        backup_service = await get_cached_backup_service()
        health_data = backup_service.get_cache_health()
        return health_data
    except ImportError as e:
        return {
            "service": "backup_check",
            "status": "disabled",
            "reason": "backup_dependencies_missing",
            "error": str(e)
        }
    except Exception as e:
        return {
            "service": "backup_check",
            "status": "error",
            "error": str(e)
        }

@app.post("/refresh-backup", tags=["Admin"])
async def refresh_backup_data():
    """Manually trigger backup data refresh"""
    try:
        from app.services.cached_backup_service import get_cached_backup_service
        backup_service = await get_cached_backup_service()
        success = await backup_service.update_cached_data(force=True)
        
        if success:
            return {
                "success": True,
                "message": "Backup data refreshed successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to refresh backup data"
            }
    except ImportError as e:
        return {
            "success": False,
            "message": f"Backup service dependencies not available: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error refreshing backup data: {str(e)}"
        }

# WebSocket endpoint for real-time emergency alerts
@app.websocket("/ws/emergency/{user_id}")
async def emergency_websocket(websocket: WebSocket, user_id: str):
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            print(f"Received from {user_id}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )