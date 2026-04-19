"""LLM 对话服务"""

import os
import httpx
from typing import Optional


class LLMService:
    """LLM 对话服务 — 支持多模型切换"""
    
    def __init__(self):
        self.default_model = os.getenv("DEFAULT_MODEL", "openrouter/anthropic/claude-sonnet-4")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    async def chat(
        self,
        system_prompt: str,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """发送对话请求"""
        model = model or self.default_model
        
        if model.startswith("openrouter/"):
            return await self._openrouter_chat(
                system_prompt, messages, model, temperature, max_tokens
            )
        elif model.startswith("anthropic/"):
            return await self._anthropic_chat(
                system_prompt, messages, model, temperature, max_tokens
            )
        else:
            return await self._openai_chat(
                system_prompt, messages, model, temperature, max_tokens
            )
    
    async def _openai_chat(self, system_prompt, messages, model, temperature, max_tokens):
        """OpenAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "model": model.replace("openai/", ""),
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *messages,
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _anthropic_chat(self, system_prompt, messages, model, temperature, max_tokens):
        """Anthropic API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": model.replace("anthropic/", ""),
                    "system": system_prompt,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            data = response.json()
            return data["content"][0]["text"]
    
    async def _openrouter_chat(self, system_prompt, messages, model, temperature, max_tokens):
        """OpenRouter API"""
        actual_model = model.replace("openrouter/", "")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openrouter_key}"},
                json={
                    "model": actual_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *messages,
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]
