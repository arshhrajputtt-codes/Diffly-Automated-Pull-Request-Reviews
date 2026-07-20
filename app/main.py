from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.review_requests import router as review_requests_router
from app.api.webhooks import router as webhooks_router
from app.core.config import settings
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered GitHub pull request reviewer",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Diffly is running", "version": settings.APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(webhooks_router)
app.include_router(review_requests_router)
