from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, emotions, chat, meditation, monitoring, training, dashboard

app = FastAPI(title="Mental Health AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(emotions.router, prefix="/emotions", tags=["Emotions"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(meditation.router, prefix="/meditation", tags=["Meditation"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(training.router, prefix="/training", tags=["Training"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Mental Health AI API"} 