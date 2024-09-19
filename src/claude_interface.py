import anthropic
from settings import ANTHROPIC_API_KEY

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
)
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content)
