import openai
from agentipy.agent import SolanaAgentKit

def create_image(agent: SolanaAgentKit, prompt: str, size: str = "1024x1024", n: int = 1):
    """
    Generate an image using OpenAI's DALL-E
    :param agent: SolanaAgentKit instance
    :param prompt: Text description of the image to generate
    :param size: Image size ('256x256', '512x512', or '1024x1024') (default: '1024x1024')
    :param n: Number of images to generate (default: 1)
    :returns: Object containing the generated image URLs
    """

    try:
        if not agent.openai_api_key:
            raise ValueError("OpenAI API key not found in agent configuration")
        
        openai.api_key = agent.openai_api_key

        response = openai.images.generate(
            prompt=prompt,
            n=n,
            size=size
        )

        return {
            "images": [img['url'] for img in response['data']]
        }
    except Exception as e:
        raise Exception(f"Image generation failed {str(e)}")
