from huggingface_hub import AsyncInferenceClient
import asyncio

client = AsyncInferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1")

async def generate_text(prompt):
    text = ""
    async for token in await client.text_generation(prompt, stream=False):
        print(token, end="", flush=True)
        text += token
    print()  # Ensure to print a newline after the full response is printed
    print(f"\n[DEBUG] Full response: {text}")

async def main_loop():
    while True:
        user_input = input("Enter your prompt (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        await generate_text(user_input)

if __name__ == "__main__":
    asyncio.run(main_loop())
