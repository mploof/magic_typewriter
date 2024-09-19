import requests

from settings import OPENAI_API_KEY

def send_test_request_to_chatgpt():
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",  # Use an appropriate model
        "prompt": "This is a test request.",
        "max_tokens": 5
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        # Reading rate limit info from the headers
        rate_limit = response.headers.get('OpenAI-Request-Units')
        rate_limit_remaining = response.headers.get('OpenAI-Request-Units-Remaining')
        rate_limit_reset = response.headers.get('OpenAI-Request-Units-Reset')

        print("Rate Limit:", rate_limit)
        print("Rate Limit Remaining:", rate_limit_remaining)
        print("Rate Limit Reset:", rate_limit_reset)
    else:
        print("Failed to get a successful response:", response.status_code)
        print(response.headers)

send_test_request_to_chatgpt()
