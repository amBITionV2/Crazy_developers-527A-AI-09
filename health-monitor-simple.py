#!/usr/bin/env python3
"""
RaktaKosh Connect Health Monitor (Simplified)
Monitors both frontend and backend servers and auto-restarts if needed
"""

import time
import subprocess
import logging
import requests
from datetime import datetime

# Configure logging without emojis for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/health-monitor.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleHealthMonitor:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:5173"
        self.check_interval = 60  # Check every 60 seconds
        self.max_failures = 3  # Restart after 3 consecutive failures
        
        self.backend_failures = 0
        self.frontend_failures = 0
        self.start_time = time.time()
        
    def check_backend_health(self):
        """Check if backend is healthy"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.backend_failures = 0
                return True
            else:
                self.backend_failures += 1
                logger.warning(f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.backend_failures += 1
            logger.warning(f"Backend health check failed: {e}")
            return False
    
    def check_frontend_health(self):
        """Check if frontend is healthy"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.frontend_failures = 0
                return True
            else:
                self.frontend_failures += 1
                logger.warning(f"Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            self.frontend_failures += 1
            logger.warning(f"Frontend health check failed: {e}")
            return False
    
    def restart_backend(self):
        """Restart the backend server"""
        try:
            logger.info("Restarting backend...")
            # Kill existing backend processes
            subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
            time.sleep(3)
            
            # Start new backend process
            subprocess.Popen([
                "python", "-m", "uvicorn", "app.main:app", 
                "--host", "127.0.0.1", "--port", "8000"
            ], cwd="bloodaid-backend")
            
            time.sleep(10)  # Wait for startup
            logger.info("Backend restart initiated")
            self.backend_failures = 0
            
        except Exception as e:
            logger.error(f"Backend restart error: {e}")
    
    def restart_frontend(self):
        """Restart the frontend server"""
        try:
            logger.info("Restarting frontend...")
            # Kill existing node processes
            subprocess.run(["taskkill", "/f", "/im", "node.exe"], capture_output=True)
            time.sleep(3)
            
            # Start new frontend process
            subprocess.Popen(["npm", "run", "dev"])
            
            time.sleep(10)  # Wait for startup
            logger.info("Frontend restart initiated")
            self.frontend_failures = 0
            
        except Exception as e:
            logger.error(f"Frontend restart error: {e}")
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Starting RaktaKosh Connect Health Monitor...")
        logger.info(f"Monitoring Backend: {self.backend_url}")
        logger.info(f"Monitoring Frontend: {self.frontend_url}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info(f"Auto-restart after {self.max_failures} consecutive failures")
        
        while True:
            try:
                # Check backend
                if self.check_backend_health():
                    logger.debug("Backend is healthy")
                else:
                    logger.warning(f"Backend unhealthy (failures: {self.backend_failures}/{self.max_failures})")
                    if self.backend_failures >= self.max_failures:
                        self.restart_backend()
                
                # Check frontend
                if self.check_frontend_health():
                    logger.debug("Frontend is healthy")
                else:
                    logger.warning(f"Frontend unhealthy (failures: {self.frontend_failures}/{self.max_failures})")
                    if self.frontend_failures >= self.max_failures:
                        self.restart_frontend()
                
                # Log status every 10 checks (10 minutes)
                uptime = int(time.time() - self.start_time)
                if uptime % 600 == 0:  # Every 10 minutes
                    logger.info(f"Monitor running for {uptime//60} minutes. Backend failures: {self.backend_failures}, Frontend failures: {self.frontend_failures}")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Health monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = SimpleHealthMonitor()
    monitor.run()