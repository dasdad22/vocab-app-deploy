from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, words, stats, analytics

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WordPass API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(words.router)
app.include_router(stats.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"name": "WordPass API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
