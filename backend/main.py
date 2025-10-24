"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router, load_knowledge_base

app = FastAPI(
    title="Visa Expert System API",
    description="オブジェクト指向エキスパートシステムによるビザ選定支援API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時に知識ベースを読み込み"""
    load_knowledge_base()


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Visa Expert System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
