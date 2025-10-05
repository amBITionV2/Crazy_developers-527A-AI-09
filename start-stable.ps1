#!/bin/bash

# RaktaKosh Connect - Stable Server Startup Script
# This script ensures both frontend and backend start reliably

echo "🚀 Starting RaktaKosh Connect Stable Servers..."

# Kill any existing processes on the ports
echo "🔧 Cleaning up existing processes..."
taskkill /F /IM node.exe /T 2>nul || echo "No Node processes to kill"
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force 2>nul || echo "No Python processes to kill"

# Wait a moment for processes to fully terminate
Start-Sleep -Seconds 3

# Start backend with PM2
echo "🔥 Starting Backend Server (Port 8003)..."
cd "C:\Users\Santhosh S\Desktop\raktakosh-connect\bloodaid-backend"
pm2 start ../ecosystem.config.json --only raktakosh-backend
pm2 save

# Wait for backend to fully start
Start-Sleep -Seconds 10

# Test backend health
echo "🏥 Testing Backend Health..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8003/health" -Method GET -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy and running!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend responded but may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend health check failed: $_" -ForegroundColor Red
}

# Start frontend with PM2
echo "🎨 Starting Frontend Server (Port 5173)..."
cd "C:\Users\Santhosh S\Desktop\raktakosh-connect"
pm2 start ecosystem.config.json --only raktakosh-frontend
pm2 save

# Wait for frontend to start
Start-Sleep -Seconds 15

# Test frontend health
echo "🌐 Testing Frontend Health..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is healthy and running!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Frontend responded but may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Frontend health check failed: $_" -ForegroundColor Red
}

# Show PM2 status
echo "📊 Current PM2 Process Status:"
pm2 status

# Show URLs
echo ""
echo "🎉 RaktaKosh Connect is now running stably!"
echo "📱 Frontend: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8003"
echo "📖 API Docs: http://localhost:8003/docs"
echo ""
echo "📋 Useful PM2 Commands:"
echo "  pm2 status          - Check process status"
echo "  pm2 restart all     - Restart all processes"
echo "  pm2 stop all        - Stop all processes"
echo "  pm2 logs            - View logs"
echo "  pm2 monit           - Monitor processes"
echo ""
echo "🔄 Both servers will auto-restart if they crash!"
echo "📝 Logs are saved in: ./logs/"