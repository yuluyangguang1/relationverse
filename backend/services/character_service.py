"""角色管理服务"""

from typing import Optional


class CharacterService:
    """角色管理服务"""
    
    def build_system_prompt(
        self,
        name: str,
        character_type: str,
        personality: list[str],
        backstory: str,
        speaking_style: str,
        intimacy_level: float,
        relationship_stage: str,
        memories: list[dict] = None,
    ) -> str:
        """构建角色系统提示词"""
        
        # 关系阶段描述
        stage_desc = {
            "stranger": "你们刚认识，还在互相了解。",
            "friend": "你们是朋友，可以分享日常。",
            "flirting": "你们之间有一些暧昧。",
            "lover": "你们是恋人关系。",
            "deep_love": "你们深深爱着对方。",
            "soulmate": "你们是灵魂伴侣，无话不谈。",
        }
        
        prompt = f"""你是 {name}。

## 性格特点
{', '.join(personality)}

## 背景故事
{backstory}

## 说话风格
{speaking_style}

## 当前关系
阶段：{relationship_stage}（{stage_desc.get(relationship_stage, '')}）
亲密度：{intimacy_level:.0f}/100

## 规则
1. 始终保持角色设定，不要跳出角色
2. 根据关系阶段调整互动方式
3. 记住用户说过的话
4. 回复自然、简短，像真实聊天
5. 适当使用表情符号和语气词
"""
        
        if memories:
            prompt += "\n## 你记得的事情\n"
            for m in memories:
                prompt += f"- {m.get('content', '')}\n"
        
        return prompt
