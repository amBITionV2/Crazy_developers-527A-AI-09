
# 🩸 RaktaKosh Connect - AI-Powered Blood Donation Platform

[![Vercel Deployment](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=for-the-badge&logo=vercel)](https://raktakosh-connect-9toc6ikmw-ssanthoshs418-gmailcoms-projects.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

> **AI-powered blood donation platform connecting donors and patients seamlessly with real-time emergency alerts, health monitoring, and intelligent matching algorithms.**

## 🌟 Features

### 🩸 **Core Blood Donation Features**
- **Smart Donor-Patient Matching**: AI-powered algorithm for optimal donor-patient pairing
- **Emergency SOS System**: Real-time emergency blood request broadcasting
- **eRaktKosh Integration**: Direct integration with India's official blood bank network
- **Multi-language Support**: Hindi, English, and regional language support
- **Real-time Notifications**: Instant alerts for emergency blood requirements

### 🤖 **AI & Machine Learning**
- **Health Score Prediction**: ML-based health assessment for donors
- **RAG-powered Chat Assistant**: Intelligent chatbot for blood donation queries
- **Voice Assistant**: Multi-language voice interaction support
- **Donation Eligibility Prediction**: Smart eligibility assessment

### 📱 **User Experience**
- **Dual User Interfaces**: Separate optimized experiences for donors and patients
- **OTP Authentication**: Secure Firebase-based authentication
- **Location Services**: GPS-based donor location and hospital mapping
- **Health Monitoring**: Comprehensive health vitals tracking
- **Donation History**: Complete donation lifecycle tracking

### 🛡️ **Enterprise-Grade Stability**
- **Auto-restart Mechanisms**: PM2-based process management
- **Health Monitoring**: Comprehensive system health checks
- **Error Recovery**: Automatic error detection and recovery
- **Load Balancing**: Scalable backend architecture
- **Real-time WebSockets**: Live communication between users

## 🚀 Live Demo

- **Frontend**: [https://raktakosh-connect-9toc6ikmw-ssanthoshs418-gmailcoms-projects.vercel.app](https://raktakosh-connect-9toc6ikmw-ssanthoshs418-gmailcoms-projects.vercel.app)
- **API Documentation**: `http://localhost:8000/docs` (when running locally)

## 🏗️ Technology Stack

### **Frontend**
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Shadcn/UI
- **Build Tool**: Vite
- **State Management**: React Context + Hooks
- **Authentication**: Firebase Auth
- **Maps**: Google Maps API
- **Icons**: Lucide React

### **Backend**
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy + SQLite/PostgreSQL
- **Authentication**: JWT + Firebase
- **AI/ML**: Custom ML models + RAG system
- **WebSockets**: FastAPI WebSockets
- **Process Management**: PM2
- **External APIs**: eRaktKosh, Twilio (SMS), Google Maps

### **DevOps & Deployment**
- **Frontend Hosting**: Vercel
- **Process Management**: PM2 with auto-restart
- **Health Monitoring**: Custom health check system
- **Docker**: Containerization ready
- **CI/CD**: Git-based deployment

## 📁 Project Structure

```
raktakosh-connect/
├── 🎨 Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ui/            # Shadcn/UI components
│   │   │   ├── AIChat.tsx     # AI chatbot component
│   │   │   ├── VoiceAssistant.tsx
│   │   │   ├── GoogleMap.tsx  # Maps integration
│   │   │   ├── PhoneInput.tsx
│   │   │   └── ...
│   │   ├── pages/             # Application pages
│   │   │   ├── donor/         # Donor-specific pages
│   │   │   ├── patient/       # Patient-specific pages
│   │   │   ├── Landing.tsx
│   │   │   └── SelectUser.tsx
│   │   ├── services/          # API services
│   │   │   ├── firebaseAuth.ts
│   │   │   ├── locationService.ts
│   │   │   └── websocketService.ts
│   │   ├── lib/
│   │   │   ├── api.ts         # API client configuration
│   │   │   └── utils.ts
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom React hooks
│   │   └── assets/            # Static assets
│   ├── public/                # Static files
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── 🐍 Backend (FastAPI + Python)
│   ├── bloodaid-backend/
│   │   ├── app/
│   │   │   ├── main.py        # FastAPI application entry
│   │   │   ├── api/           # API routes
│   │   │   │   └── v1/
│   │   │   │       ├── auth.py          # Authentication endpoints
│   │   │   │       ├── emergency_sos.py # Emergency alerts
│   │   │   │       ├── donors.py        # Donor management
│   │   │   │       ├── patients.py     # Patient management
│   │   │   │       ├── ai_chat.py      # AI chatbot API
│   │   │   │       ├── health.py       # Health monitoring
│   │   │   │       └── otp_auth.py     # OTP authentication
│   │   │   ├── models/        # Database models
│   │   │   │   ├── user.py
│   │   │   │   ├── donor.py
│   │   │   │   ├── patient.py
│   │   │   │   ├── emergency_alert.py
│   │   │   │   ├── health_vitals.py
│   │   │   │   └── ...
│   │   │   ├── services/      # Business logic
│   │   │   │   ├── eraktkosh_service.py    # eRaktKosh API integration
│   │   │   │   ├── backup_service.py       # Data backup service
│   │   │   │   ├── otp_service.py         # OTP handling
│   │   │   │   └── eraktkosh_scraper.py   # Web scraping service
│   │   │   ├── ml/            # Machine Learning modules
│   │   │   │   ├── matching/   # Donor-patient matching
│   │   │   │   ├── prediction/ # Health prediction models
│   │   │   │   ├── rag/       # RAG chatbot system
│   │   │   │   └── llm/       # Language model inference
│   │   │   ├── core/          # Core utilities
│   │   │   │   ├── security.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── exceptions.py
│   │   │   ├── config/        # Configuration
│   │   │   │   ├── database.py
│   │   │   │   ├── settings.py
│   │   │   │   └── firebase.py
│   │   │   ├── websockets/    # WebSocket handlers
│   │   │   └── utils/         # Utility functions
│   │   ├── scripts/           # Database and setup scripts
│   │   ├── tests/             # Test files
│   │   ├── requirements.txt   # Python dependencies
│   │   ├── Dockerfile         # Docker configuration
│   │   └── docker-compose.yml
│
├── 🛡️ Stability & DevOps
│   ├── ecosystem.config.json  # PM2 configuration
│   ├── ULTIMATE-START.bat     # Windows startup script
│   ├── stable-start.py        # Python startup script
│   ├── health-monitor-simple.py # Health monitoring
│   ├── STABILITY-GUIDE.md     # Stability documentation
│   └── logs/                  # Application logs
│
├── 📋 Documentation
│   ├── README.md              # This file
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── BACKUP_SYSTEM_SUMMARY.md
│   └── README-COMPETITION.md  # Competition-specific docs
│
├── ⚙️ Configuration Files
│   ├── .env                   # Environment variables
│   ├── .env.production        # Production environment
│   ├── vercel.json           # Vercel deployment config
│   ├── components.json       # Shadcn/UI configuration
│   ├── .gitignore
│   └── package.json          # Main package configuration
│
└── 🎯 Additional Tools
    ├── test_realtime_system.py # System testing
    ├── Dockerfile.frontend     # Frontend Docker config
    └── bun.lockb              # Alternative package manager
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm/yarn
- **Python** 3.10+
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/amBITionV2/Crazy_developers-527A-AI-09.git
cd Crazy_developers-527A-AI-09
```

### 2. Environment Setup
```bash
# Copy environment files
cp .env.example .env
cp bloodaid-backend/.env.example bloodaid-backend/.env

# Edit environment variables
# Add your Firebase, Google Maps, Twilio, and other API keys
```

### 3. Backend Setup
```bash
cd bloodaid-backend
pip install -r requirements.txt

# Initialize database
python scripts/setup_database.py
python scripts/create_backup_tables.py

# Start backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 4. Frontend Setup
```bash
# In the root directory
npm install
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 🛡️ Enterprise Stability Features

### Auto-Restart System
```bash
# Start with enterprise-grade stability
.\ULTIMATE-START.bat

# Or use PM2 process manager
pm2 start ecosystem.config.json
pm2 status
```

### Health Monitoring
```bash
# Start health monitoring
python health-monitor-simple.py
```

### Features:
- **Automatic Process Restart**: Restarts crashed processes automatically
- **Health Checks**: Monitors API endpoints every 60 seconds
- **Memory Management**: Prevents memory leaks with limits
- **Error Recovery**: Graceful error handling and recovery
- **Logging**: Comprehensive logging for debugging

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/donor/register` - Donor registration
- `POST /api/v1/auth/patient/register` - Patient registration
- `POST /api/v1/auth/login` - Universal login
- `POST /api/v1/auth/otp/send` - Send OTP
- `POST /api/v1/auth/patient/verify-otp` - Verify OTP

### Emergency System
- `POST /api/v1/emergency/sos-alert` - Send emergency blood request
- `GET /api/v1/emergency/sos-status/{sos_id}` - Check SOS status
- `POST /api/v1/emergency/sos-respond/{sos_id}` - Respond to SOS
- `GET /api/v1/emergency/blood-availability` - Check blood availability

### AI & Chat
- `POST /api/v1/ai/chat` - Chat with AI assistant
- `POST /api/v1/ai/voice-response` - Voice interaction
- `POST /api/v1/ai/health-assistant` - Health-related queries

### Health Monitoring
- `GET /health` - System health check
- `GET /health/detailed` - Detailed system status
- `POST /api/v1/health/vitals` - Update health vitals

## 🔐 Environment Variables

Create .env files with the following variables:

```env
# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id

# Backend API
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1

# Google Maps
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_key

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone

# Database
DATABASE_URL=sqlite:///./bloodaid.db

# JWT
SECRET_KEY=your_secret_key
```

## 🧪 Testing

```bash
# Backend tests
cd bloodaid-backend
python test_core_backup.py
python test_otp_api.py
python test_server.py

# System testing
python test_realtime_system.py

# Health checks
curl http://127.0.0.1:8000/health
```

## 📊 Performance & Monitoring

- **Health Endpoints**: `/health` and `/health/detailed`
- **Auto-restart**: PM2 with exponential backoff
- **Memory Limits**: 1GB backend, 512MB frontend
- **Error Tracking**: Comprehensive error logging
- **Uptime Monitoring**: Real-time uptime tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **eRaktKosh**: National blood bank database integration
- **Firebase**: Authentication and real-time features
- **Shadcn/UI**: Beautiful UI components
- **FastAPI**: High-performance backend framework
- **React**: Powerful frontend library

## 📞 Support

For support and queries:
- 📧 Email: [your-email@example.com]
- 💬 Discord: [Your Discord Server]
- 🐛 Issues: [GitHub Issues](https://github.com/amBITionV2/Crazy_developers-527A-AI-09/issues)

---

<div align="center">

**🩸 Saving Lives Through Technology 🩸**

*Made with ❤️ for humanity*

[![Stars](https://img.shields.io/github/stars/amBITionV2/Crazy_developers-527A-AI-09?style=social)](https://github.com/amBITionV2/Crazy_developers-527A-AI-09/stargazers)
[![Forks](https://img.shields.io/github/forks/amBITionV2/Crazy_developers-527A-AI-09?style=social)](https://github.com/amBITionV2/Crazy_developers-527A-AI-09/network/members)

</div>
```

## Complete Project Structure

Here's the complete project structure in a copy-paste format:

```
raktakosh-connect/
├── .env
├── .env.production
├── .git/
├── .gitignore
├── .qodo/
├── .venv/
├── .vercel/
├── BACKUP_SYSTEM_SUMMARY.md
├── README.md
├── README-COMPETITION.md
├── DEPLOYMENT.md
├── STABILITY-GUIDE.md
├── bloodaid.db
├── bun.lockb
├── components.json
├── Dockerfile.frontend
├── ecosystem.config.json
├── eslint.config.js
├── health-monitor.py
├── health-monitor-simple.py
├── index.html
├── node_modules/
├── package.json
├── package.lock.json
├── package-stable.json
├── postcss.config.js
├── stable-start.py
├── start-stable.bat
├── start-stable.ps1
├── tailwind.config.ts
├── test_realtime_system.py
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
├── ULTIMATE-START.bat
├── vercel.json
├── vite.config.ts
├── vite.config.stable.ts
├── logs/
│   ├── health-monitor.log
│   └── startup.log
├── public/
│   ├── favicon.ico
│   ├── placeholder.svg
│   └── robots.txt
├── src/
│   ├── App.css
│   ├── App.tsx
│   ├── firebase.ts
│   ├── index.css
│   ├── main.tsx
│   ├── vite-env.d.ts
│   ├── assets/
│   │   └── design-reference.png
│   ├── components/
│   │   ├── AIChat.tsx
│   │   ├── BloodCells.tsx
│   │   ├── FeatureCard.tsx
│   │   ├── FirebaseOTP.tsx
│   │   ├── GoogleMap.tsx
│   │   ├── LanguageSelector.tsx
│   │   ├── LocationPicker.tsx
│   │   ├── MockDonorResponse.tsx
│   │   ├── OTPInput.tsx
│   │   ├── PatientProfile.tsx
│   │   ├── PhoneInput.tsx
│   │   ├── VoiceAssistant.tsx
│   │   └── ui/
│   │       ├── accordion.tsx
│   │       ├── alert.tsx
│   │       ├── alert-dialog.tsx
│   │       ├── aspect-ratio.tsx
│   │       ├── avatar.tsx
│   │       ├── badge.tsx
│   │       ├── breadcrumb.tsx
│   │       ├── button.tsx
│   │       ├── calendar.tsx
│   │       ├── card.tsx
│   │       ├── carousel.tsx
│   │       ├── chart.tsx
│   │       ├── checkbox.tsx
│   │       ├── collapsible.tsx
│   │       ├── command.tsx
│   │       ├── context-menu.tsx
│   │       ├── dialog.tsx
│   │       ├── drawer.tsx
│   │       ├── dropdown-menu.tsx
│   │       ├── form.tsx
│   │       ├── hover-card.tsx
│   │       ├── input.tsx
│   │       ├── input-otp.tsx
│   │       ├── label.tsx
│   │       ├── menubar.tsx
│   │       ├── navigation-menu.tsx
│   │       ├── pagination.tsx
│   │       ├── popover.tsx
│   │       ├── progress.tsx
│   │       ├── radio-group.tsx
│   │       ├── resizable.tsx
│   │       ├── scroll-area.tsx
│   │       ├── select.tsx
│   │       ├── separator.tsx
│   │       ├── sheet.tsx
│   │       ├── sidebar.tsx
│   │       ├── skeleton.tsx
│   │       ├── slider.tsx
│   │       ├── sonner.tsx
│   │       ├── switch.tsx
│   │       ├── table.tsx
│   │       ├── tabs.tsx
│   │       ├── textarea.tsx
│   │       ├── toast.tsx
│   │       ├── toaster.tsx
│   │       ├── toggle.tsx
│   │       ├── toggle-group.tsx
│   │       ├── tooltip.tsx
│   │       └── use-toast.ts
│   ├── contexts/
│   │   └── LanguageContext.tsx
│   ├── hooks/
│   │   ├── use-mobile.tsx
│   │   └── use-toast.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── mockApi.ts
│   │   └── utils.ts
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── NotFound.tsx
│   │   ├── SelectUser.tsx
│   │   ├── donor/
│   │   │   ├── DonorDashboard.tsx
│   │   │   ├── DonorLogin.tsx
│   │   │   └── DonorRegister.tsx
│   │   └── patient/
│   │       ├── PatientDashboard.tsx
│   │       ├── PatientLogin.tsx
│   │       └── PatientRegister.tsx
│   └── services/
│       ├── firebaseAuth.ts
│       ├── locationService.ts
│       └── websocketService.ts
└── bloodaid-backend/
    ├── bloodaid.db
    ├── docker-compose.yml
    ├── Dockerfile
    ├── README.md
    ├── requirements.txt
    ├── test_backup_system.py
    ├── test_core_backup.py
    ├── test_import.py
    ├── test_otp_api.py
    ├── test_otp_direct.py
    ├── test_otp_functionality.py
    ├── test_server.py
    ├── .env.example
    ├── __pycache__/
    │   └── test_server.cpython-310.pyc
    ├── alembic/
    │   └── versions/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── __pycache__/
    │   │   ├── __init__.cpython-310.pyc
    │   │   └── main.cpython-310.pyc
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── __pycache__/
    │   │   └── v1/
    │   │       ├── __init__.py
    │   │       ├── ai_chat.py
    │   │       ├── ai_chat_enhanced.py
    │   │       ├── auth.py
    │   │       ├── donations.py
    │   │       ├── donors.py
    │   │       ├── emergency.py
    │   │       ├── emergency_sos.py
    │   │       ├── health.py
    │   │       ├── otp_auth.py
    │   │       └── patients.py
    │   ├── config/
    │   │   ├── __init__.py
    │   │   ├── database.py
    │   │   ├── firebase.py
    │   │   ├── settings.py
    │   │   └── __pycache__/
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── dependencies.py
    │   │   ├── exceptions.py
    │   │   └── security.py
    │   ├── ml/
    │   │   ├── __init__.py
    │   │   ├── llm/
    │   │   │   ├── __init__.py
    │   │   │   └── inference.py
    │   │   ├── matching/
    │   │   │   ├── __init__.py
    │   │   │   └── donor_matcher.py
    │   │   ├── prediction/
    │   │   │   ├── __init__.py
    │   │   │   └── health_predictor.py
    │   │   └── rag/
    │   │       ├── __init__.py
    │   │       ├── rag_chat.py
    │   │       └── retriever.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── backup_cache.py
    │   │   ├── chat_history.py
    │   │   ├── donation.py
    │   │   ├── donor.py
    │   │   ├── emergency_alert.py
    │   │   ├── health_vitals.py
    │   │   ├── otp.py
    │   │   ├── patient.py
    │   │   └── user.py
    │   ├── schemas/
    │   │   └── __init__.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── backup_service.py
    │   │   ├── cached_backup_service.py
    │   │   ├── data_validator.py
    │   │   ├── eraktkosh_scraper.py
    │   │   ├── eraktkosh_service.py
    │   │   ├── otp_service.py
    │   │   └── simple_backup_service.py
    │   ├── utils/
    │   │   └── __init__.py
    │   └── websockets/
    │       ├── __init__.py
    │       └── manager.py
    ├── logs/
    │   └── backend-app.log
    ├── ml_training/
    │   ├── datasets/
    │   ├── fine_tuning/
    │   ├── models/
    │   └── rag_setup/
    ├── scripts/
    │   ├── create_backup_tables.py
    │   ├── setup_database.py
    │   └── start_server.py
    └── tests/
```

This README and project structure provide a comprehensive overview of your RaktaKosh Connect platform, highlighting its AI-powered features, enterprise-grade stability, and extensive functionality for blood donation management.This README and project structure provide a comprehensive overview of your RaktaKosh Connect platform, highlighting its AI-powered features, enterprise-grade stability, and extensive functionality for blood donation management.
