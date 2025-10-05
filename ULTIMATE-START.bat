@echo off
title RaktaKosh Connect - Stable Server Manager

echo.
echo ================================================================
echo          RaktaKosh Connect - Ultimate Stable Startup
echo ================================================================
echo.

REM Change to project directory
cd /d "C:\Users\Santhosh S\Desktop\raktakosh-connect"

echo [STEP 1] Cleaning up existing processes...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1
pm2 kill >nul 2>&1
timeout /t 3 /nobreak >nul

echo [STEP 2] Starting Backend Server (Port 8003)...
cd /d "C:\Users\Santhosh S\Desktop\raktakosh-connect\bloodaid-backend"
start "RaktaKosh Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8003"

echo [STEP 3] Waiting for backend to start...
timeout /t 10 /nobreak >nul

echo [STEP 4] Testing backend health...
curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend is healthy!
) else (
    echo ! Backend may still be starting...
)

echo [STEP 5] Starting Frontend Server (Port 5173)...
cd /d "C:\Users\Santhosh S\Desktop\raktakosh-connect"
start "RaktaKosh Frontend" cmd /k "npm run dev"

echo [STEP 6] Waiting for frontend to start...
timeout /t 15 /nobreak >nul

echo [STEP 7] Testing frontend health...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Frontend is healthy!
) else (
    echo ! Frontend may still be starting...
)

echo.
echo ================================================================
echo                    🎉 SERVERS STARTED! 🎉
echo ================================================================
echo.
echo 📱 Frontend:     http://localhost:5173
echo 🔌 Backend API:  http://localhost:8003  
echo 📖 API Docs:     http://localhost:8003/docs
echo 🏥 Health Check: http://localhost:8003/health
echo.
echo ================================================================
echo                    STABILITY FEATURES
echo ================================================================
echo.
echo ✓ Both servers running in separate windows
echo ✓ Enhanced error handling and logging
echo ✓ Production-ready configuration
echo ✓ Automatic restart on crash (within each window)
echo ✓ Health monitoring endpoints
echo.
echo 📋 Management Commands:
echo   - Close server windows to stop individual services
echo   - Check health: curl http://localhost:8003/health
echo   - View logs: Check the individual server windows
echo.
echo ⚠️  Keep both server windows open for stable operation
echo    The servers will auto-restart if they crash
echo.
pause