from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_input: int
    tokens_output: int
    finish_reason: str
    metadata: Dict[str, Any]


class LLMGateway:
    def __init__(self, providers: Optional[Dict[str, Any]] = None):
        self.providers = providers or {}
        self.default_provider = "openai"

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        return LLMResponse(
            content="LLM response placeholder - configure provider to enable",
            model=model or "unknown",
            provider=provider or self.default_provider,
            tokens_input=0,
            tokens_output=0,
            finish_reason="stop",
            metadata={},
        )

    async def generate_with_context(
        self,
        query: str,
        context: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        system_prompt = (
            "You are a research assistant. Use the provided context to answer questions. "
            "Always cite your sources and distinguish between evidence and inference."
        )

        prompt = f"Context:\n{context}\n\nQuestion: {query}"

        return await self.generate(
            prompt=prompt,
            model=model,
            provider=provider,
            system_prompt=system_prompt,
            **kwargs,
        )

    async def embed(
        self,
        texts: List[str],
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> List[List[float]]:
        return [[0.0] * 1536 for _ in texts]

    async def classify(
        self,
        text: str,
        categories: List[str],
        model: Optional[str] = None,
    ) -> Dict[str, float]:
        return {cat: 1.0 / len(categories) for cat in categories}

    def set_provider(self, task: str, provider: str, model: str, **kwargs):
        self.providers[task] = {
            "provider": provider,
            "model": model,
            **kwargs,
        }

    def get_provider(self, task: str) -> Optional[Dict[str, Any]]:
        return self.providers.get(task)
