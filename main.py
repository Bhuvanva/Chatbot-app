import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.routes.test_routes import router as test_router
from app.routes.lab_routes import router as lab_router
from chatbot.main4 import router as whatsapp_router

load_dotenv()

API_PREFIX = "/api/v1"

# Lifespan of fast api server
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    yield
    print("Shutting down application...")
# Properly close all connections

app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from React frontend
allow_origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Include routers
app.include_router(test_router, prefix=f"{API_PREFIX}/tests", tags=["tests"])
app.include_router(lab_router, prefix=f"{API_PREFIX}/labs", tags=["labs"])
app.include_router(whatsapp_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LabBuddy ChatBot"}
