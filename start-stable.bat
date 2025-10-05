@echo off
REM RaktaKosh Connect - Windows Batch Startup Script
REM This script provides a simple way to start stable servers

echo 🚀 Starting RaktaKosh Connect Stable Servers...

REM Clean up existing processes
echo 🔧 Cleaning up existing processes...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

REM Wait for cleanup
timeout /t 3 /nobreak >nul

REM Change to project directory
cd /d "C:\Users\Santhosh S\Desktop\raktakosh-connect"

REM Start both services with PM2
echo 🔥 Starting Backend and Frontend with PM2...
pm2 start ecosystem.config.json
pm2 save

REM Wait for services to start
timeout /t 20 /nobreak >nul

REM Show status
echo 📊 Current Process Status:
pm2 status

echo.
echo 🎉 RaktaKosh Connect is now running stably!
echo 📱 Frontend: http://localhost:5173
echo 🔌 Backend API: http://localhost:8003
echo 📖 API Docs: http://localhost:8003/docs
echo.
echo 🔄 Both servers will auto-restart if they crash!
echo 📝 Use 'pm2 logs' to view logs
echo.
pause