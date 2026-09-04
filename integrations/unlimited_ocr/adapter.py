from typing import Optional, Dict, Any


class OCRAdapter:
    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        self.endpoint = endpoint
        self.api_key = api_key

    async def extract_text(
        self, file_path: str, language: str = "en"
    ) -> Optional[str]:
        return None

    async def extract_from_image(
        self, image_data: bytes, language: str = "en"
    ) -> Optional[str]:
        return None

    async def extract_from_pdf(
        self, pdf_path: str, language: str = "en"
    ) -> Optional[str]:
        return None
