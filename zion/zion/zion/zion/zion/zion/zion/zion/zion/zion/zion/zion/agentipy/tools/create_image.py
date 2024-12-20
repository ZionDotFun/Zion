from typing import Dict, Optional, List
from dataclasses import dataclass
import aiohttp
import base64
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

@dataclass
class ImageGenerationResult:
    """Holds the result of image generation."""
    url: str
    revised_prompt: Optional[str] = None
    base64_data: Optional[str] = None

class ImageGenerator:
    """Utility class for generating and managing images."""

    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required.")
        self.openai_api_key = openai_api_key
        self._generated_images: List[ImageGenerationResult] = []

    async def generate_image(
        self, 
        prompt: str, 
        size: str = "1024x1024", 
        quality: str = "standard", 
        style: str = "natural", 
        save_to_disk: bool = False
    ) -> ImageGenerationResult:
        """
        Generates an image using OpenAI's DALL-E API.

        Args:
            prompt: Description of the desired image.
            size: Image size ("1024x1024", "1024x1792", "1792x1024").
            quality: Image quality ("standard" or "hd").
            style: Image style ("natural" or "vivid").
            save_to_disk: Save the generated image locally.

        Returns:
            ImageGenerationResult with details of the generated image.
        """
        valid_sizes = ["1024x1024", "1024x1792", "1792x1024"]
        valid_qualities = ["standard", "hd"]
        valid_styles = ["natural", "vivid"]

        if size not in valid_sizes:
            raise ValueError(f"Invalid size. Choose from {valid_sizes}.")
        if quality not in valid_qualities:
            raise ValueError(f"Invalid quality. Choose from {valid_qualities}.")
        if style not in valid_styles:
            raise ValueError(f"Invalid style. Choose from {valid_styles}.")

        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            "style": style,
            "response_format": "url"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_detail = await response.text()
                        raise Exception(f"OpenAI API error: {error_detail}")

                    data = await response.json()
                    image_url = data['data'][0]['url']
                    revised_prompt = data['data'][0].get('revised_prompt')

                    if save_to_disk:
                        await self._save_image_to_disk(image_url, prompt)

                    result = ImageGenerationResult(url=image_url, revised_prompt=revised_prompt)
                    self._generated_images.append(result)
                    return result
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise

    async def get_image_as_base64(self, image_url: str) -> str:
        """
        Converts an image from a URL to a base64 string.

        Args:
            image_url: URL of the image to convert.

        Returns:
            Base64 encoded string of the image.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download image: HTTP {response.status}")

                    image_data = await response.read()
                    return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {str(e)}")
            raise

    async def optimize_image_size(
        self, 
        image_url: str, 
        max_size_kb: int = 500
    ) -> str:
        """
        Optimizes an image to fit within the specified size limit.

        Args:
            image_url: URL of the image to optimize.
            max_size_kb: Maximum allowed size in kilobytes.

        Returns:
            Base64 encoded optimized image.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    image_data = await response.read()

            image = Image.open(io.BytesIO(image_data))
            buffer = io.BytesIO()
            quality = 95

            while len(buffer.getvalue()) / 1024 > max_size_kb and quality > 50:
                buffer.seek(0)
                buffer.truncate()
                image.save(buffer, format='PNG', optimize=True, quality=quality)
                quality -= 5

            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to optimize image: {str(e)}")
            raise

    async def _save_image_to_disk(self, image_url: str, prompt: str) -> str:
        """
        Downloads and saves an image to the local file system.

        Args:
            image_url: URL of the image to download.
            prompt: Description of the image for naming the file.

        Returns:
            The local file path of the saved image.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download image: HTTP {response.status}")

                    image_data = await response.read()

                    safe_filename = "".join(c for c in prompt if c.isalnum() or c in "._- ")[:50]
                    filename = f"generated_image_{safe_filename}.png"

                    with open(filename, "wb") as file:
                        file.write(image_data)

                    return filename
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            raise

    def get_generation_history(self) -> List[ImageGenerationResult]:
        """Returns a list of all previously generated images."""
        return self._generated_images.copy()
