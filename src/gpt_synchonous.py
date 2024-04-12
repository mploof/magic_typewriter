###### Standard Imports ######
import yaml

###### Third-Party Imports ######
from openai import OpenAI

###### Local Imports ######
from bias import get_bias
import settings
from settings import config
import images

###### Global Vars ######
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_synchonous_response(
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
