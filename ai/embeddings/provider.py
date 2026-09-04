from typing import List, Optional
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        pass

    @abstractmethod
    def get_dimensions(self) -> int:
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.dimensions = 1536

    async def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * self.dimensions for _ in texts]

    async def embed_query(self, query: str) -> List[float]:
        return [0.0] * self.dimensions

    def get_dimensions(self) -> int:
        return self.dimensions


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_path: str, dimensions: int = 384):
        self.model_path = model_path
        self.dimensions = dimensions

    async def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * self.dimensions for _ in texts]

    async def embed_query(self, query: str) -> List[float]:
        return [0.0] * self.dimensions

    def get_dimensions(self) -> int:
        return self.dimensions
