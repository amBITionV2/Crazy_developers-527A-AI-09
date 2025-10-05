from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "BloodAid Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "BloodAid"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./bloodaid.db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "bloodaid_db"
    DATABASE_USER: str = "username"
    DATABASE_PASSWORD: str = "password"
    
    # Security Settings
    SECRET_KEY: str = "bloodaid-super-secret-key-for-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    ALLOWED_CREDENTIALS: bool = True
    ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    ALLOWED_HEADERS: str = "*"
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = ""
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    
    # AI/ML Configuration
    OPENAI_API_KEY: str = ""
    GROK_API_KEY: str = ""
    GROK_API_BASE: str = "https://api.x.ai/v1"
    GROK_BASE_URL: str = "https://api.x.ai/v1"
    DEFAULT_AI_MODEL: str = "grok-beta"
    ENABLE_RAG: bool = False
    CHROMADB_PERSIST_DIRECTORY: str = "./data/chromadb"
    
    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Firebase Configuration for Authentication
    FIREBASE_API_KEY: str = ""
    FIREBASE_AUTH_DOMAIN: str = ""
    FIREBASE_MESSAGING_SENDER_ID: str = ""
    FIREBASE_APP_ID: str = ""
    
    # OTP Configuration
    OTP_LENGTH: int = 6
    OTP_EXPIRY_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3
    ENABLE_OTP_SMS: bool = True
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@bloodaid.app"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Monitoring and Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_PROMETHEUS: bool = False
    PROMETHEUS_PORT: int = 8001
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760
    UPLOAD_DIRECTORY: str = "./uploads"
    ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,image/gif,application/pdf"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = 30
    ENABLE_HEALTH_CHECKS: bool = True
    
    # Backup Configuration
    BACKUP_ENABLED: bool = False
    BACKUP_SCHEDULE: str = "0 2 * * *"
    BACKUP_RETENTION_DAYS: int = 30
    
    # Legacy fields for backward compatibility
    LLM_MODEL_PATH: str = "./models/bloodaid-llm-finetuned"
    RAG_DB_PATH: str = "./rag_database"
    USE_RAG: bool = False
    ERAKTKOSH_API_KEY: Optional[str] = None
    ERAKTKOSH_BASE_URL: str = "https://api.eraktkosh.in"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields instead of ignore

settings = Settings()