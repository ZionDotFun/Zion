import openai

from agentipy.agent import SolanaAgentKit


class ImageGenerator:
    @staticmethod
    async def create_image(agent:SolanaAgentKit, prompt, size="1024x1024", n=1):
        try:
            if not agent.openai_api_key:
                raise ValueError("OpenAI API key not found in agent configuration")

            openai.api_key = agent.openai_api_key

            response = await openai.Image.create(
                prompt=prompt,
                n=n,
                size=size
            )

            return {
                "images": [img['url'] for img in response['data']]
            }

        except Exception as error:
            raise Exception(f"Image generation failed: {str(error)}")
