"""
RelationVerse — AI 关系宇宙
FastAPI 后端主入口
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from api.routes import chat, characters, pets, memorial, auth, users, upload
from database.engine import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await init_db()
    print("🚀 RelationVerse 后端启动完成")
    print(f"📡 API 文档: http://{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}/docs")
    yield
    # 关闭时
    await close_db()
    print("👋 RelationVerse 后端已关闭")


app = FastAPI(
    title="RelationVerse API",
    description="AI 关系宇宙 — 恋人 · 朋友 · 家人 · 宠物 · 导师",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（上传的文件）
os.makedirs("data/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(characters.router, prefix="/api/characters", tags=["角色"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(pets.router, prefix="/api/pets", tags=["宠物"])
app.include_router(memorial.router, prefix="/api/memorial", tags=["数字怀念"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])


@app.get("/")
async def root():
    return {
        "name": "RelationVerse",
        "version": "0.1.0",
        "description": "AI 关系宇宙 — 让每个人拥有真实的情感连接",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
