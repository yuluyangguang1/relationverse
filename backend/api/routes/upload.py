"""文件上传 API 路由"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

UPLOAD_DIR = "data/uploads"
ALLOWED_EXTENSIONS = {
    "photos": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "voices": {".mp3", ".wav", ".m4a", ".ogg", ".flac"},
    "memories": {".txt", ".md", ".json"},
}


@router.post("/photo")
async def upload_photo(file: UploadFile = File(...)):
    """上传照片"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS["photos"]:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, "photos", filename)
    
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    
    return {
        "url": f"/uploads/photos/{filename}",
        "filename": filename,
        "size": len(content),
    }


@router.post("/voice")
async def upload_voice(file: UploadFile = File(...)):
    """上传语音"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS["voices"]:
        raise HTTPException(status_code=400, detail="不支持的音频格式")
    
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, "voices", filename)
    
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    
    return {
        "url": f"/uploads/voices/{filename}",
        "filename": filename,
        "size": len(content),
    }
