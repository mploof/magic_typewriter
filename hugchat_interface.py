from huggingface_hub import AsyncInferenceClient
import asyncio

async def main_thread():
    client = AsyncInferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1")
    async for token in await client.text_generation("How do you make cheese?", stream=True):
        print(token, end="", flush=True)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main_thread())
