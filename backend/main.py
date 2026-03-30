from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, data, dashboard, recommendations, records, profile, estimation
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="健康减肥推荐系统API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(data.router)
app.include_router(dashboard.router)
app.include_router(recommendations.router)
app.include_router(records.router)
app.include_router(profile.router)
app.include_router(estimation.router)   # ✅ 确保此行存在

@app.get("/")
def root():
    return {"message": "健康减肥推荐系统API v2.0运行中"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0"}