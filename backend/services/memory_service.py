"""记忆服务"""

from typing import Optional


class MemoryService:
    """记忆管理服务 — 长期记忆 + 语义检索"""
    
    def __init__(self):
        # TODO: 连接 Qdrant
        pass
    
    async def store_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        character_id: Optional[str] = None,
        tags: list[str] = None,
    ):
        """存储记忆"""
        # TODO: 生成 embedding → 存入 Qdrant
        pass
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        character_id: Optional[str] = None,
    ) -> list[dict]:
        """语义检索相关记忆"""
        # TODO: query embedding → Qdrant 搜索
        return []
    
    async def get_recent_memories(
        self,
        user_id: str,
        limit: int = 10,
        character_id: Optional[str] = None,
    ) -> list[dict]:
        """获取最近的记忆"""
        return []
