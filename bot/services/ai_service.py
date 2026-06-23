from typing import List, Dict, Any, AsyncGenerator
from bot.config import settings
from bot.utils import logger
import httpx
import json


class AIService:
    def __init__(self):
        self.api_key = settings.API_KEY
        self.base_url = settings.BASE_URL
        self.model = settings.MODEL

    def build_messages(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        system_prompt: str = "",
    ) -> List[Dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
    ) -> AsyncGenerator[str, None]:
        model = model or self.model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST", self.base_url, headers=headers, json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk["choices"][0]["delta"]
                                if "content" in delta and delta["content"]:
                                    yield delta["content"]
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
        except httpx.HTTPStatusError as e:
            logger.error(f"خطأ HTTP من واجهة الذكاء الاصطناعي: {e}")
            yield "❌ خطأ في الاتصال بالذكاء الاصطناعي. يرجى المحاولة لاحقاً."
        except Exception as e:
            logger.error(f"خطأ غير متوقع في الذكاء الاصطناعي: {e}")
            yield "❌ حدث خطأ. يرجى المحاولة مرة أخرى."

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
    ) -> str:
        model = model or self.model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(self.base_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"خطأ في خدمة الذكاء الاصطناعي: {e}")
            return "❌ حدث خطأ في المعالجة. يرجى المحاولة لاحقاً."
