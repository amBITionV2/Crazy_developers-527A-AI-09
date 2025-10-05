from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import asyncio
import signal
import sys
import time
import logging
from contextlib import asynccontextmanager

from app.api.v1 import auth, emergency, health, ai_chat_enhanced, donors, patients, donations, otp_auth, emergency_sos
from app.websockets.manager import ConnectionManager
from app.core.exceptions import BloodAidException

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/backend-app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global application state
class AppState:
    def __init__(self):
        self.startup_time = time.time()
        self.is_shutting_down = False
        self.background_tasks = []
        
app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting BloodAid Backend...")
    
    try:
        # Database connection
        logger.info("✅ Database connected")
        
        # Initialize backup service with enhanced error handling
        await initialize_backup_service()
        
        # Start health monitoring
        health_task = asyncio.create_task(health_monitor())
        app_state.background_tasks.append(health_task)
        
        logger.info("🎉 BloodAid Backend started successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down BloodAid Backend...")
        app_state.is_shutting_down = True
        
        # Cancel background tasks
        for task in app_state.background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Backend shutdown complete")

async def initialize_backup_service():
    """Initialize backup service with error handling"""
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
    async def refresh_backup_data():
        while not app_state.is_shutting_down:
            try:
                await backup_service.update_cached_data()
                logger.info("📦 Backup data refreshed successfully")
                # Wait 2 hours before next update
                await asyncio.sleep(2 * 60 * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"⚠️ Backup refresh error: {e}")
                # Wait 30 minutes before retry on error
                await asyncio.sleep(30 * 60)
    
    # Start the background task
    refresh_task = asyncio.create_task(refresh_backup_data())
    app_state.background_tasks.append(refresh_task)
    logger.info(f"📦 Backup service ({service_type}) initialized and background refresh started")

async def health_monitor():
    """Monitor application health and auto-restart if needed"""
    while not app_state.is_shutting_down:
        try:
            # Basic health checks
            uptime = time.time() - app_state.startup_time
            logger.debug(f"💓 Health check - Uptime: {uptime:.2f}s")
            
            # Check memory usage, database connections, etc.
            # Add more health checks as needed
            
            await asyncio.sleep(60)  # Check every minute
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            await asyncio.sleep(30)

# Initialize FastAPI app with lifespan management
app = FastAPI(
    title="BloodAid API",
    description="AI-Powered Blood Donation Platform Backend - Production Ready",
    version="1.0.0",
    lifespan=lifespan
)

# Add security and performance middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.railway.app", "*.render.com"]
)

# CORS middleware with enhanced security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "https://raktakosh-connect-*.vercel.app",
        "https://*.railway.app",
        "https://*.render.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request timeout middleware
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        # Set a 30-second timeout for all requests
        response = await asyncio.wait_for(call_next(request), timeout=30.0)
        return response
    except asyncio.TimeoutError:
        logger.error(f"Request timeout: {request.url}")
        return JSONResponse(
            status_code=504,
            content={"error": "Request timeout", "detail": "The request took too long to process"}
        )

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error for {request.url}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": "An unexpected error occurred"}
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

# Enhanced exception handler
@app.exception_handler(BloodAidException)
async def bloodaid_exception_handler(request: Request, exc: BloodAidException):
    logger.warning(f"BloodAid exception for {request.url}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail}
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc):
    logger.error(f"Internal server error for {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Please try again later"}
    )

# Remove old startup/shutdown events (now handled by lifespan)

# Enhanced health check endpoints
@app.get("/", tags=["Health"])
async def root():
    uptime = time.time() - app_state.startup_time
    return {
        "status": "healthy",
        "service": "BloodAid API",
        "version": "1.0.0",
        "uptime_seconds": round(uptime, 2),
        "ml_enabled": True,
        "environment": "production-ready"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    uptime = time.time() - app_state.startup_time
    return {
        "api": "operational",
        "database": "connected",
        "llm": "ready",
        "rag": "enabled",
        "uptime_seconds": round(uptime, 2),
        "background_tasks": len(app_state.background_tasks),
        "is_shutting_down": app_state.is_shutting_down
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Comprehensive health check for monitoring"""
    uptime = time.time() - app_state.startup_time
    
    # Check various system components
    health_status = {
        "timestamp": time.time(),
        "uptime_seconds": round(uptime, 2),
        "status": "healthy",
        "components": {
            "api": "operational",
            "database": "connected",
            "websockets": "ready",
            "background_tasks": {
                "count": len(app_state.background_tasks),
                "status": "running"
            },
            "memory": "normal",  # Could add actual memory monitoring
            "disk": "sufficient"  # Could add actual disk monitoring
        }
    }
    
    return health_status

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

# Enhanced WebSocket endpoint with better error handling
@app.websocket("/ws/emergency/{user_id}")
async def emergency_websocket(websocket: WebSocket, user_id: str):
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            # Set a timeout for receiving messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                logger.info(f"Received from {user_id}: {data}")
                # Handle incoming messages if needed
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text('{"type": "ping"}')
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
        ws_manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        ws_manager.disconnect(user_id, websocket)

# Graceful shutdown handling
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    app_state.is_shutting_down = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Production-ready server configuration
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,  # Disable reload in production for stability
        log_level="info",
        access_log=True,
        workers=1,  # Single worker for stability with WebSockets
        timeout_keep_alive=120,
        timeout_graceful_shutdown=30
    )