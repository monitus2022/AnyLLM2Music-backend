from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(title="AnyLLM2Music", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anyllm2music-frontend.pages.dev", "https://music.monitus.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1/music")