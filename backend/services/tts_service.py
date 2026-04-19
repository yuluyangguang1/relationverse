"""TTS 语音合成服务"""

import os
import uuid
import subprocess
from typing import Optional


class TTSService:
    """TTS 语音合成服务"""
    
    def __init__(self):
        self.output_dir = "data/uploads/tts"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def synthesize(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",  # Edge TTS 声音
        speed: float = 1.0,
    ) -> str:
        """合成语音并返回文件路径"""
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(self.output_dir, filename)
        
        # 使用 edge-tts（免费）
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice, rate=f"{int((speed - 1) * 100):+d}%")
            await communicate.save(output_path)
            return f"/uploads/tts/{filename}"
        except ImportError:
            # 回退到系统 tts（macOS）
            subprocess.run(["say", "-o", output_path, text], check=True)
            return f"/uploads/tts/{filename}"
    
    def get_available_voices(self) -> list[dict]:
        """获取可用声音列表"""
        return [
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "gender": "female", "lang": "zh"},
            {"id": "zh-CN-YunxiNeural", "name": "云希", "gender": "male", "lang": "zh"},
            {"id": "zh-CN-YunjianNeural", "name": "云健", "gender": "male", "lang": "zh"},
            {"id": "zh-CN-XiaoyiNeural", "name": "晓伊", "gender": "female", "lang": "zh"},
            {"id": "zh-CN-YunyangNeural", "name": "云扬", "gender": "male", "lang": "zh"},
            {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "female", "lang": "en"},
            {"id": "en-US-GuyNeural", "name": "Guy", "gender": "male", "lang": "en"},
        ]
