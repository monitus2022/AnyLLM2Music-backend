from fastapi import FastAPI
from .routes import router

app = FastAPI(title="AnyLLM2Music", version="0.1.0")

app.include_router(router)