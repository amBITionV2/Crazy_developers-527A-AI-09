# BloodAid Backend

Complete AI-powered blood donation platform backend built with FastAPI, featuring advanced ML capabilities, real-time WebSocket communication, and comprehensive donor-patient matching.

## 🩸 Features

### Core Features
- **User Management**: Registration, authentication, and role-based access (donors/patients)
- **Emergency Alerts**: Real-time SOS system with WebSocket notifications
- **Health Tracking**: Comprehensive vital signs monitoring and eligibility assessment
- **Smart Matching**: AI-powered donor-patient matching algorithm
- **Donation Management**: Complete donation lifecycle tracking
- **Multilingual Support**: English, Hindi, Kannada, Telugu, Malayalam

### AI/ML Capabilities
- **Grok LLM Integration**: Advanced conversational AI with context awareness
- **RAG (Retrieval Augmented Generation)**: Medical knowledge base for accurate responses
- **Health Predictions**: Donation eligibility and risk assessment
- **Smart Notifications**: Intelligent alert prioritization

### Real-time Features
- **WebSocket Support**: Live emergency alerts and notifications
- **Location Services**: GPS-based donor discovery
- **Live Chat**: AI-powered multilingual assistance

## 🏗️ Architecture

```
bloodaid-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/v1/              # API endpoints
│   │   ├── auth.py          # Authentication & registration
│   │   ├── emergency.py     # Emergency SOS alerts
│   │   ├── health.py        # Health vitals tracking
│   │   ├── ai_chat_enhanced.py  # AI chat with RAG
│   │   ├── donors.py        # Donor management
│   │   ├── patients.py      # Patient management
│   │   └── donations.py     # Donation tracking
│   ├── models/              # Database models
│   │   ├── user.py          # Base user model
│   │   ├── donor.py         # Donor profiles
│   │   ├── patient.py       # Patient profiles
│   │   ├── emergency_alert.py  # Emergency alerts
│   │   ├── donation.py      # Donation records
│   │   ├── health_vitals.py # Health tracking
│   │   └── chat_history.py  # AI chat logs
│   ├── ml/                  # AI/ML modules
│   │   ├── llm/             # Language model integration
│   │   ├── rag/             # Retrieval augmented generation
│   │   ├── prediction/      # Health prediction models
│   │   └── matching/        # Donor matching algorithms
│   ├── core/                # Core utilities
│   │   ├── security.py      # JWT authentication
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── exceptions.py    # Custom exceptions
│   ├── config/              # Configuration
│   │   ├── settings.py      # App settings
│   │   ├── database.py      # Database setup
│   │   └── firebase.py      # Firebase configuration
│   └── websockets/          # WebSocket manager
├── ml_training/             # ML training scripts
├── tests/                   # Test suites
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── .env.example           # Environment template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)
- Docker & Docker Compose (recommended)

### Environment Setup

1. **Clone and navigate to backend**
```bash
cd bloodaid-backend
```

2. **Copy environment configuration**
```bash
cp .env.example .env
```

3. **Update .env file with your credentials**
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/bloodaid_db

# AI APIs
GROK_API_KEY=your-grok-api-key
OPENAI_API_KEY=your-openai-api-key

# Firebase
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_CREDENTIALS_PATH=path/to/service-account.json

# Security
SECRET_KEY=your-super-secret-key
```

### Docker Deployment (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bloodaid-backend

# Stop services
docker-compose down
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/setup_database.py

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.bloodaid.app`

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Authentication
```
POST /api/v1/auth/register    # User registration
POST /api/v1/auth/login       # User login
POST /api/v1/auth/refresh     # Token refresh
GET  /api/v1/auth/me          # Current user info
```

#### Emergency System
```
POST /api/v1/emergency/sos              # Create SOS alert
GET  /api/v1/emergency/alerts           # Get nearby alerts
PUT  /api/v1/emergency/alerts/{id}      # Update alert status
```

#### AI Chat
```
POST /api/v1/ai/chat                    # Chat with AI assistant
GET  /api/v1/ai/chat-history/{user_id}  # Get chat history
GET  /api/v1/ai/health-check            # AI service status
```

#### Health Tracking
```
POST /api/v1/health/vitals              # Record health vitals
GET  /api/v1/health/vitals              # Get health history
POST /api/v1/health/eligibility-check   # Check donation eligibility
```

#### Donor Management
```
GET  /api/v1/donors/search              # Search donors
POST /api/v1/donors/profile             # Update donor profile
GET  /api/v1/donors/nearby              # Find nearby donors
```

### WebSocket Endpoints
```
WS /ws/emergency                        # Emergency alerts
WS /ws/notifications/{user_id}          # Personal notifications
```

## 🤖 AI/ML Features

### Grok LLM Integration
- **Multilingual Support**: 5 languages with context-aware responses
- **Medical Knowledge**: Specialized in blood donation and health topics
- **Emergency Detection**: Automatic urgency assessment

### RAG System
- **Medical Knowledge Base**: Curated medical information
- **Context Retrieval**: Relevant document fetching
- **Response Enhancement**: Knowledge-augmented answers

### Prediction Models
- **Eligibility Assessment**: Health-based donation eligibility
- **Risk Analysis**: Health risk prediction
- **Trend Analysis**: Health parameter tracking

### Smart Matching
- **Compatibility Scoring**: Blood type compatibility matrix
- **Distance Optimization**: Geographic proximity scoring
- **Availability Assessment**: Real-time donor availability
- **Reliability Metrics**: Historical donation patterns

## 🔧 Configuration

### Database Models
- **Users**: Base authentication and profiles
- **Donors**: Donor-specific information and preferences
- **Patients**: Patient profiles and medical history
- **Emergency Alerts**: SOS requests and responses
- **Donations**: Complete donation lifecycle
- **Health Vitals**: Comprehensive health tracking
- **Chat History**: AI conversation logs

### Security Features
- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt encryption
- **Role-based Access**: Donor/patient permissions
- **Rate Limiting**: API abuse prevention
- **CORS Configuration**: Cross-origin security

### Monitoring & Logging
- **Health Checks**: Service status monitoring
- **Structured Logging**: Comprehensive log management
- **Prometheus Metrics**: Performance monitoring
- **Error Tracking**: Exception management

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test module
pytest tests/test_auth.py

# Run integration tests
pytest tests/integration/
```

## 📊 Performance

### Optimization Features
- **Async Operations**: Non-blocking I/O
- **Connection Pooling**: Database connection management
- **Caching**: Redis-based response caching
- **Batch Processing**: Efficient bulk operations
- **Background Tasks**: Asynchronous processing

### Scaling Considerations
- **Horizontal Scaling**: Multiple container instances
- **Load Balancing**: Nginx reverse proxy
- **Database Sharding**: Multi-database support
- **CDN Integration**: Static asset delivery

## 🔒 Security

### Best Practices
- **Environment Variables**: Secure configuration management
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Input sanitization
- **CSRF Protection**: Cross-site request forgery prevention
- **Secure Headers**: Security-focused HTTP headers

### Authentication Flow
1. User registration with email verification
2. Password hashing with bcrypt
3. JWT token generation and validation
4. Role-based access control
5. Token refresh mechanism

## 🚀 Deployment

### Production Checklist
- [ ] Update environment variables
- [ ] Configure SSL certificates
- [ ] Set up database backups
- [ ] Configure monitoring
- [ ] Set up logging
- [ ] Configure rate limiting
- [ ] Update CORS settings
- [ ] Set up health checks

### Docker Production
```bash
# Build production image
docker build -t bloodaid-backend:latest .

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Production
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.bloodaid.app](https://docs.bloodaid.app)
- **Issues**: [GitHub Issues](https://github.com/bloodaid/backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bloodaid/backend/discussions)
- **Email**: support@bloodaid.app

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Powerful ORM
- **Grok AI**: Advanced language model
- **PostgreSQL**: Robust database system
- **Docker**: Containerization platform