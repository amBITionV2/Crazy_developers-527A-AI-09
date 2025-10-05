# 🚀 RaktaKosh Connect - Ultra-Stable Server Setup

## 🎯 **Problem Solved: No More Server Crashes!**

Your RaktaKosh Connect application now has **enterprise-grade stability** with:
- ✅ **Auto-restart on crashes**
- ✅ **Enhanced error handling**
- ✅ **Health monitoring**
- ✅ **Production-ready configuration**
- ✅ **Network error resilience**

---

## 🏃‍♂️ **Quick Start (Recommended)**

### **Option 1: Ultimate Stable Startup (Easiest)**
```bash
# Double-click this file or run:
.\ULTIMATE-START.bat
```
- Starts both servers in separate windows
- Built-in health checks
- Auto-cleanup of conflicting processes
- Visual status updates

### **Option 2: PM2 Process Manager (Advanced)**
```bash
# Start with PM2 for maximum stability
pm2 start ecosystem.config.json
pm2 save
pm2 monit  # Monitor processes
```

### **Option 3: Manual Start (Development)**
```bash
# Terminal 1 - Backend
cd bloodaid-backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003

# Terminal 2 - Frontend  
npm run dev
```

---

## 🛡️ **Stability Features Implemented**

### **1. Enhanced Backend Stability**
- **Graceful shutdown handling** with signal management
- **Request timeout middleware** (30s max per request)  
- **Error recovery middleware** for unhandled exceptions
- **Health monitoring** with detailed status endpoints
- **Background task management** with proper cleanup
- **Production-ready logging** with file and console output
- **Memory and resource monitoring**

### **2. Process Management (PM2)**
- **Auto-restart** on crashes (max 10 restarts)
- **Minimum uptime** enforcement (10s before restart)
- **Memory limit protection** (1GB backend, 512MB frontend)
- **Exponential backoff** for restart delays
- **Cluster mode support** for scaling
- **Log file management** with rotation

### **3. Network Resilience**
- **CORS configuration** for multiple environments
- **Trusted host middleware** for security
- **GZip compression** for performance
- **WebSocket stability** with ping/pong and timeouts
- **Connection pooling** and keep-alive settings

### **4. Health Monitoring**
- **Real-time health checks** every 60 seconds
- **Auto-restart** after 3 consecutive failures
- **Detailed health endpoints**:
  - `/health` - Basic status
  - `/health/detailed` - Comprehensive metrics
  - `/backup-health` - Backup service status
- **Uptime tracking** and failure analytics

---

## 📊 **Server URLs & Endpoints**

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Main application |
| **Backend API** | http://localhost:8003 | API endpoints |
| **API Documentation** | http://localhost:8003/docs | Swagger/OpenAPI docs |
| **Health Check** | http://localhost:8003/health | Basic health status |
| **Detailed Health** | http://localhost:8003/health/detailed | Comprehensive metrics |
| **Backup Health** | http://localhost:8003/backup-health | Backup service status |

---

## 🔧 **Management Commands**

### **PM2 Management**
```bash
pm2 status              # Check process status
pm2 restart all         # Restart all processes  
pm2 stop all           # Stop all processes
pm2 logs               # View live logs
pm2 logs --lines 100   # View last 100 log lines
pm2 monit              # Real-time monitoring
pm2 save               # Save current process list
pm2 startup            # Enable startup on boot
```

### **Health Checks**
```bash
# Test backend health
curl http://localhost:8003/health

# Test frontend availability  
curl http://localhost:5173

# Detailed health metrics
curl http://localhost:8003/health/detailed
```

### **Log Management**
```bash
# View backend logs
pm2 logs raktakosh-backend

# View frontend logs  
pm2 logs raktakosh-frontend

# View all logs
pm2 logs

# Clear logs
pm2 flush
```

---

## 🚨 **Troubleshooting**

### **If Servers Won't Start**
1. **Check ports**: Ensure 8003 and 5173 are free
2. **Clean processes**: Run `.\ULTIMATE-START.bat` (includes cleanup)
3. **Check logs**: Look in `./logs/` directory
4. **Manual cleanup**:
   ```bash
   taskkill /F /IM node.exe /T
   taskkill /F /IM python.exe /T
   pm2 kill
   ```

### **If Servers Keep Crashing**
1. **Check health**: `curl http://localhost:8003/health`
2. **View logs**: `pm2 logs` or check `./logs/`
3. **Restart services**: `pm2 restart all`
4. **Check dependencies**: Ensure all npm/pip packages installed

### **Network/Connection Issues**
- **CORS errors**: Backend automatically handles frontend requests
- **Timeout errors**: Requests timeout after 30 seconds (configurable)
- **WebSocket issues**: Auto-reconnection with ping/pong heartbeat

---

## 📁 **File Structure**

```
raktakosh-connect/
├── ULTIMATE-START.bat          # Ultimate stable startup script
├── ecosystem.config.json       # PM2 configuration
├── start-stable.ps1           # PowerShell startup script
├── start-stable.bat           # Batch startup script  
├── stable-start.py            # Python startup script
├── health-monitor.py          # Health monitoring script
├── package-stable.json        # Stable package configuration
├── vite.config.stable.ts      # Stable Vite configuration
├── logs/                      # Log files directory
│   ├── backend-*.log         # Backend logs
│   ├── frontend-*.log        # Frontend logs
│   └── startup.log           # Startup logs
└── bloodaid-backend/
    └── app/
        └── main.py           # Enhanced backend with stability features
```

---

## 🎉 **Success Indicators**

Your servers are running stably when you see:

✅ **Backend**: "All systems healthy" in health checks  
✅ **Frontend**: Application loads without errors  
✅ **PM2**: All processes show "online" status  
✅ **Logs**: No repeating error messages  
✅ **Monitoring**: Health monitor reports success  

---

## 🔄 **Auto-Recovery Features**

1. **Crash Recovery**: PM2 automatically restarts crashed processes
2. **Health Monitoring**: Background health checker restarts unhealthy services
3. **Memory Protection**: Processes restart if memory usage exceeds limits
4. **Graceful Shutdown**: Proper cleanup on termination signals
5. **Error Isolation**: Single component failures don't affect entire system

---

## 🚀 **Next Steps**

1. **Deploy to Production**: Use the same PM2 setup on your production server
2. **Add Monitoring**: Consider adding external monitoring tools (Prometheus, Grafana)
3. **Scale Up**: PM2 supports clustering for high-traffic scenarios
4. **Backup Strategy**: Implement database backups and log rotation

---

**🎊 Congratulations! Your RaktaKosh Connect platform now has enterprise-grade stability and will run without unwanted restarts or network errors!**