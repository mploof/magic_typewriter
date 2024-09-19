###### Standard Imports ######
import yaml

###### Third-Party Imports ######
from openai import OpenAI
import anthropic

###### Local Imports ######
from bias import get_bias
import settings
from settings import config, ANTHROPIC_API_KEY
import images

###### Global Vars ######
if settings.ai == "anthropic":
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_claude_synchonous_response(
    prompt=None,
    messages=None,
    model=config["chat_model"],
    max_tokens=config["max_tokens"],
    temperature=config["chat_temperature"],
    image_url=None,
    image_name=None,
):
    print("Getting Claude response.")
    if messages is None:
        
        messages = []
        
        if image_name is not None:
            extension = image_name.split(".")[-1]
            if extension == "jpg":
                media_type = "image/jpeg"
            else:
                media_type = f"image/{extension}" 
        
            messages = [{"role": "user", "content": [
                {
                    "type": "image",
                    "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": images.get_base64_image(image_name),
                    }
                },
                {"type": "text", "text": prompt}
            ]}]
        else:
            messages = [{"role": "user", "content": prompt}]
    
    response = client.messages.create(
        model="claude-3-opus-20240229",
        # model="claude-3-sonnet-20240229",
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature,
    )
    with open('response.yaml', 'w') as file:
        yaml.dump(response, file)
    return response.content[0].text

def get_gpt_synchonous_response(
    prompt=None,
    messages=None,
    model=config["chat_model"],
    max_tokens=config["max_tokens"],
    temperature=config["chat_temperature"],
    image_url=None,
    image_name=None,
    logit_bias={}
):
    
    if image_name is not None:
        image_url = images.get_base64_image_url(image_name)
    
    if messages is None:
        content = []
        if image_url is not None:
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        if prompt is not None:
            content.append({"type": "text", "text": prompt})
        if len(content) == 0:
            print('No content provided for GPT request.')
            return ""
        messages = [{"role": "user", "content": content}]
       
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        logit_bias=logit_bias
    )
    with open('response.yaml', 'w') as file:
        yaml.dump(response, file)
    return response.choices[0].message.content

def get_synchronous_response(
    prompt=None,
    messages=None,
    model=config["chat_model"],
    max_tokens=config["max_tokens"],
    temperature=config["chat_temperature"],
    image_url=None,
    image_name=None,
    logit_bias={}):
    
    if settings.ai == "anthropic":
        return get_claude_synchonous_response(prompt=prompt, messages=messages, max_tokens=max_tokens, temperature=temperature, image_url=image_url, image_name=image_name)
    else:
        return get_gpt_synchonous_response(prompt, messages, model, max_tokens, temperature, image_url, image_name, logit_bias)