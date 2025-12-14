from fastapi import FastAPI
from dotenv import load_dotenv

from src.routes.root import router

load_dotenv()

app = FastAPI(title="Template FastAPI", version="0.1.0")

app.include_router(router)