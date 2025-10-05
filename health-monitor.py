#!/usr/bin/env python3
"""
RaktaKosh Connect Health Monitor
Monitors both frontend and backend servers and auto-restarts if needed
"""

import asyncio
import aiohttp
import time
import subprocess
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/health-monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.backend_url = "http://localhost:8003"
        self.frontend_url = "http://localhost:5173"
        self.check_interval = 60  # Check every 60 seconds
        self.max_failures = 3  # Restart after 3 consecutive failures
        self.backend_failures = 0
        self.frontend_failures = 0
        self.start_time = time.time()
        
    async def check_backend_health(self):
        """Check if backend is healthy"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Backend health: {data}")
                        return True
                    else:
                        logger.warning(f"Backend health check failed: Status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Backend health check error: {e}")
            return False

    async def check_frontend_health(self):
        """Check if frontend is healthy"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(self.frontend_url) as response:
                    if response.status == 200:
                        logger.debug("Frontend is responding")
                        return True
                    else:
                        logger.warning(f"Frontend health check failed: Status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Frontend health check error: {e}")
            return False

    def restart_backend(self):
        """Restart backend using PM2"""
        try:
            logger.info("🔄 Restarting backend...")
            result = subprocess.run(
                ["pm2", "restart", "raktakosh-backend"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("✅ Backend restarted successfully")
                return True
            else:
                logger.error(f"❌ Backend restart failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend restart error: {e}")
            return False

    def restart_frontend(self):
        """Restart frontend using PM2"""
        try:
            logger.info("🔄 Restarting frontend...")
            result = subprocess.run(
                ["pm2", "restart", "raktakosh-frontend"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("✅ Frontend restarted successfully")
                return True
            else:
                logger.error(f"❌ Frontend restart failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Frontend restart error: {e}")
            return False

    def get_pm2_status(self):
        """Get PM2 process status"""
        try:
            result = subprocess.run(
                ["pm2", "jlist"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to get PM2 status: {e}")
            return None

    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🏥 Starting RaktaKosh Connect Health Monitor...")
        
        while True:
            try:
                # Check backend health
                backend_healthy = await self.check_backend_health()
                if backend_healthy:
                    self.backend_failures = 0
                    logger.debug("✅ Backend is healthy")
                else:
                    self.backend_failures += 1
                    logger.warning(f"❌ Backend unhealthy (failures: {self.backend_failures}/{self.max_failures})")
                    
                    if self.backend_failures >= self.max_failures:
                        logger.error("🚨 Backend has failed too many times, attempting restart...")
                        if self.restart_backend():
                            self.backend_failures = 0
                            # Wait for backend to start
                            await asyncio.sleep(10)

                # Check frontend health
                frontend_healthy = await self.check_frontend_health()
                if frontend_healthy:
                    self.frontend_failures = 0
                    logger.debug("✅ Frontend is healthy")
                else:
                    self.frontend_failures += 1
                    logger.warning(f"❌ Frontend unhealthy (failures: {self.frontend_failures}/{self.max_failures})")
                    
                    if self.frontend_failures >= self.max_failures:
                        logger.error("🚨 Frontend has failed too many times, attempting restart...")
                        if self.restart_frontend():
                            self.frontend_failures = 0
                            # Wait for frontend to start
                            await asyncio.sleep(15)

                # Log overall status
                uptime = time.time() - self.start_time
                if backend_healthy and frontend_healthy:
                    logger.info(f"💓 All systems healthy - Uptime: {uptime:.0f}s")

                # Get PM2 status for detailed monitoring
                pm2_status = self.get_pm2_status()
                if pm2_status:
                    for process in pm2_status:
                        if process['name'] in ['raktakosh-backend', 'raktakosh-frontend']:
                            status = process['pm2_env']['status']
                            restarts = process['pm2_env']['restart_time']
                            logger.debug(f"PM2 {process['name']}: {status} (restarts: {restarts})")

                # Wait before next check
                await asyncio.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("🛑 Health monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.check_interval)

async def main():
    monitor = HealthMonitor()
    await monitor.monitor_loop()

if __name__ == "__main__":
    asyncio.run(main())