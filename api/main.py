from fastapi import FastAPI
from app.auth import router as auth_router
from app.model import router as model_router

app = FastAPI(
    title="Insurance Chatbot API",
    description="Interactive chatbot",
    version="1.0.0",
    docs_url="/docs",  
    redoc_url="/redoc"
)

app.include_router(auth_router.router)
app.include_router(model_router.router)