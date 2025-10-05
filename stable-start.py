#!/usr/bin/env python3
"""
RaktaKosh Connect - Ultimate Stable Startup Script
Starts both servers with comprehensive error handling and monitoring
"""

import subprocess
import time
import sys
import os
import signal
import requests
import logging
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/startup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StableStartup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_port = 8003
        self.frontend_port = 5173
        self.max_startup_wait = 120  # 2 minutes max startup time
        self.health_check_retries = 30  # 30 attempts with 2s intervals
        
    def cleanup_processes(self):
        """Clean up any existing processes"""
        logger.info("🧹 Cleaning up existing processes...")
        
        try:
            # Stop PM2 processes first
            subprocess.run(["pm2", "stop", "all"], capture_output=True, timeout=10)
            subprocess.run(["pm2", "delete", "all"], capture_output=True, timeout=10)
            time.sleep(2)
            
            # Kill any remaining Node.js processes
            subprocess.run(["taskkill", "/F", "/IM", "node.exe", "/T"], 
                         capture_output=True, shell=True)
            
            # Kill any remaining Python processes on our ports
            subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], 
                         capture_output=True, shell=True)
            
            time.sleep(3)
            logger.info("✅ Process cleanup completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning (may be normal): {e}")

    def check_port_available(self, port):
        """Check if a port is available"""
        try:
            result = subprocess.run(
                ["netstat", "-ano", "|", "findstr", f":{port}"],
                capture_output=True,
                text=True,
                shell=True,
                timeout=5
            )
            return result.returncode != 0  # Port is available if netstat finds nothing
        except Exception:
            return True  # Assume available if check fails

    def wait_for_backend(self):
        """Wait for backend to be healthy"""
        logger.info("⏳ Waiting for backend to start...")
        
        for attempt in range(self.health_check_retries):
            try:
                response = requests.get(
                    f"http://localhost:{self.backend_port}/health",
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("✅ Backend is healthy!")
                    return True
            except Exception:
                pass
            
            time.sleep(2)
            logger.debug(f"Backend check attempt {attempt + 1}/{self.health_check_retries}")
        
        logger.error("❌ Backend failed to start within timeout")
        return False

    def wait_for_frontend(self):
        """Wait for frontend to be healthy"""
        logger.info("⏳ Waiting for frontend to start...")
        
        for attempt in range(self.health_check_retries):
            try:
                response = requests.get(
                    f"http://localhost:{self.frontend_port}",
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("✅ Frontend is healthy!")
                    return True
            except Exception:
                pass
            
            time.sleep(2)
            logger.debug(f"Frontend check attempt {attempt + 1}/{self.health_check_retries}")
        
        logger.error("❌ Frontend failed to start within timeout")
        return False

    def start_with_pm2(self):
        """Start both services using PM2"""
        logger.info("🚀 Starting services with PM2...")
        
        try:
            # Start PM2 ecosystem
            result = subprocess.run(
                ["pm2", "start", "ecosystem.config.json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"PM2 start failed: {result.stderr}")
                return False
            
            # Save PM2 configuration
            subprocess.run(["pm2", "save"], capture_output=True, timeout=10)
            
            logger.info("✅ PM2 services started")
            return True
            
        except Exception as e:
            logger.error(f"PM2 startup error: {e}")
            return False

    def start_health_monitor(self):
        """Start the health monitoring script"""
        try:
            logger.info("🏥 Starting health monitor...")
            
            # Start health monitor as a background process
            subprocess.Popen(
                [sys.executable, "health-monitor.py"],
                cwd=self.project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info("✅ Health monitor started")
            return True
            
        except Exception as e:
            logger.error(f"Health monitor startup error: {e}")
            return False

    def display_status(self):
        """Display the final status and URLs"""
        logger.info("📊 Getting PM2 status...")
        
        try:
            result = subprocess.run(
                ["pm2", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(result.stdout)
        except Exception as e:
            logger.error(f"Failed to get PM2 status: {e}")

        print("\n" + "="*60)
        print("🎉 RaktaKosh Connect is running stably!")
        print("="*60)
        print(f"📱 Frontend:     http://localhost:{self.frontend_port}")
        print(f"🔌 Backend API:  http://localhost:{self.backend_port}")
        print(f"📖 API Docs:     http://localhost:{self.backend_port}/docs")
        print(f"🏥 Health Check: http://localhost:{self.backend_port}/health")
        print("="*60)
        print("\n📋 Useful Commands:")
        print("  pm2 status          - Check process status")
        print("  pm2 restart all     - Restart all processes")
        print("  pm2 stop all        - Stop all processes")
        print("  pm2 logs            - View logs")
        print("  pm2 monit           - Monitor processes")
        print("\n🔄 Auto-restart: ON")
        print("🏥 Health monitoring: ON")
        print("📝 Logs location: ./logs/")
        print("="*60)

    def run(self):
        """Main startup sequence"""
        logger.info("🚀 Starting RaktaKosh Connect with Ultimate Stability...")
        
        try:
            # Step 1: Cleanup
            self.cleanup_processes()
            
            # Step 2: Check ports
            if not self.check_port_available(self.backend_port):
                logger.error(f"Port {self.backend_port} is not available!")
                return False
            
            if not self.check_port_available(self.frontend_port):
                logger.error(f"Port {self.frontend_port} is not available!")
                return False
            
            # Step 3: Start with PM2
            if not self.start_with_pm2():
                logger.error("Failed to start with PM2")
                return False
            
            # Step 4: Wait for backend
            if not self.wait_for_backend():
                logger.error("Backend startup failed")
                return False
            
            # Step 5: Wait for frontend
            if not self.wait_for_frontend():
                logger.error("Frontend startup failed")
                return False
            
            # Step 6: Start health monitor
            self.start_health_monitor()
            
            # Step 7: Display status
            self.display_status()
            
            logger.info("🎉 Startup completed successfully!")
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Startup interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            return False

def main():
    startup = StableStartup()
    success = startup.run()
    
    if success:
        print("\n✅ RaktaKosh Connect is running stably!")
        print("Press Ctrl+C to stop all services")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            subprocess.run(["pm2", "stop", "all"], capture_output=True)
            subprocess.run(["pm2", "delete", "all"], capture_output=True)
            print("✅ All services stopped")
    else:
        print("❌ Startup failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()