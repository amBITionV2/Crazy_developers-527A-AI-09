from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a simple test FastAPI app
app = FastAPI(title="Test BloodAid API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Test BloodAid API"}

@app.get("/health")
async def health_check():
    return {"api": "operational", "database": "connected"}

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)