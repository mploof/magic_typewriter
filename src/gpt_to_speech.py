###### Standard Imports ######
import asyncio
import json
import threading
import queue
import base64
from time import time

###### Third-Party Imports ######
from openai import AsyncOpenAI
import xi_labs
from xi_labs import voices
from PIL import Image
from loguru import logger

###### Local Imports ######
import listener
from bias import get_bias
import settings
from settings import get_config
import images
import audio

###### Global Vars ######


# Set OpenAI API key
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
conversations = {}
current_conversation = None
wake_word_queue = queue.Queue()


###### Classes ######

class Conversation:
    
    def __init__(self,
                name,
                voice_id=None,
                initial_context=None
    ):
        self.name = name
        if voice_id is None and name in voices.keys():
            self.voice_id = voices[name]
        else:
            self.voice_id = voice_id
            if voice_id not in voices.values():
                print("Voice ID not found. Using default voice ID.")
                self.voice_id = voices[get_config()["default_voice"]]
        
        self.context = initial_context
        self.messages = []
        self.clear_conversation()
        
    def get_context(self):
        if self.context is None:
            try:
                with open(f"./{settings.context_dir}/{self.name}_context.txt", "r") as f:
                    self.context = f.read().strip()
            except FileNotFoundError:
                print(f"Context file for {self.name} not found. Using default context")
                self.context = settings.default_context + " Your name is " + self.name + "."
        return self.context
    
    def add_message(self, role, content):
        self.get_messages()
        self.messages.append({'role': role, 'content': content})
        # Save the messages to a JSON file
        with open(f"./{settings.context_dir}/{self.name}_messages.json", "w") as f:
            # pretty print the JSON to file
            json.dump(self.messages, f, indent=4)
        
    def get_messages(self):
        # Read the messages from file
        try:
            with open(f"./{settings.context_dir}/{self.name}_messages.json", "r") as f:
                self.messages = json.load(f)
        except FileNotFoundError:
            pass
        return self.messages
    
    def save_conversation(self, file_name):
        with open(f"./{settings.context_dir}/{file_name}", "w") as f:
            json.dump(self.messages, f, indent=4)
            
    def load_conversation(self, file_name):
        with open(f"./{settings.context_dir}/{file_name}", "r") as f:
            self.messages = json.load(f)
    
    def clear_conversation(self):
        print(f"Resetting conversation with {self.name}...")
        self.messages = []
        self.messages.append({'role': 'user', 'content': self.get_context()})
        self.save_conversation(f"{self.name}_messages.json")
    
    def undo(self):
        print("Undoing last message...")
        # Remove the last assistant and user messages
        self.messages.pop()
        self.messages.pop()
        
    def activate(self):
        print(f"Activating conversation with {self.name}...")
        wake_word_queue.put(self.name)


###### Functions ######

async def text_chunker(chunks):

    buffer = ''  # Initialize the sentence as an empty string
    async for text in chunks:
        
        # Strip any leading space to avoid unwanted spaces before punctuation
        starts_with_space = text.startswith(' ')
        text = text.lstrip()
        try:
            if text.startswith(' " '):
                text = ' "' + text[3:]
            if buffer.endswith(' "') and text[0].isalpha():
                buffer += text
            elif buffer and (buffer == '' or buffer == ' ' or (not starts_with_space and buffer[-1].isalpha() and text[0].isalpha())):
                buffer += text
            elif buffer and not buffer.endswith(' ') and (not text.startswith((' ', "'", '"', ',', '.', '?', '!', ';', ':', '—', '-', '(', ')', '[', ']', '}')) or starts_with_space):
                # If the sentence does not end with a space and the element does not start with a punctuation or space,
                # add a space before the element
                buffer += ' ' + text
            else:
                # Otherwise, append the element directly to the sentence
                buffer += text
        except IndexError:
            buffer += text
        
        if buffer.endswith(('.', '?', '!', ';', ':', '—', '-', '(', ')', '[', ']', '}', " ")):
            yield buffer
            buffer = ' '

    if buffer:
        yield buffer.strip()


async def chat_completion(
    conversation:Conversation,
    model=get_config()["chat_model"],
    temperature=get_config()["chat_temperature"],
    max_tokens=get_config()["max_tokens"],
    logit_bias={}
):
    """Send a chat completion request to the OpenAI API and stream the returned text.
    The returned stream is handled depending on the output mode set in the config file.
    The chat completion parameters are set by default in the config file, but can be
    overridden by passing the desired values as arguments to this function.

    Args:
        conversation (Conversation): The conversation object to be used for the chat completion
        model (str, optional): The model to be used for the chat completion. Defaults to config["chat_model"].
        temperature (float, optional): The temperature to be used for the chat completion. Defaults to config["chat_temperature"].
        max_tokens (int, optional): The maximum number of tokens to be generated. Defaults to config["max_tokens"].
    Yields:
        _type_: _description_
    """
    response = await aclient.chat.completions.create(
        model=model,
        messages=conversation.get_messages(),
        temperature=temperature,
        stream=True,
        max_tokens=max_tokens,
        logit_bias=logit_bias
    )
    
    async def text_iterator():
        
        this_message = ""
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content is not None:
                this_message += delta.content
                yield delta.content
            else:
                continue
        conversation.add_message('assistant', this_message) # Update conversation history

    if get_config()["chat_output_mode"] == "voice":
        if get_config()["stream_output"]:
            await xi_labs.text_stream_to_speech_stream(
                text_iterator(), 
                text_chunker,
                conversation.voice_id,
                break_phrases=["TRANSCRIPT:"]
            )
        else:
            last_output = ""
            async for chunk in text_chunker(text_iterator()):
                last_output += chunk
            print(last_output)
            xi_labs.text_to_speech(
                last_output,
                conversation.voice_id,
            )
            # Play output.mp3
            await audio.play_file("output.mp3")
            
    else:
        last_output = ""
        async for chunk in text_chunker(text_iterator()):
            print(chunk, end="", sep="", flush=True)
            last_output += chunk
        print("\n")
        return last_output

last_word_time = 0
holding_prompt = ""
def transcript_parser_task(transcript_queue, prompt_queue, terminate_flag):
    """Parses the real-time voice input transcript to identify the wake word,
    and extracts the prompt to be sent to the chatbot. This function is meant
    to be run in a separate thread.

    Args:
        transcript_queue (_type_): Queue holding contents of the audio listener transcript
        prompt_queue (_type_): Queue holding the prompts to be sent to the chatbot
        terminate_flag (_type_): Flag to signal the termination of the parser thread
    """
    
    global holding_prompt
    global last_word_time
    
    current_wake_word = get_config()["override_wake_word"]
    override_wake_word = get_config()["override_wake_word"]
    
    # This is a task that runs in a loop within a separate thread
    while True:
    
        # Check if the wake word has been changed
        if not wake_word_queue.empty():
            current_wake_word = wake_word_queue.get()  
            
        # Get the current transcript from the queue
        transcript, status = transcript_queue.get()
        transcript = json.loads(transcript)
        
        if status == "final":
            # Print the finalized voice input for debugging purposes
            print("F:", transcript['text'])
            last_word_time = time()
            
            # Check for the presence of the wake word in the transcript, and if found, extract the prompt
            if get_config()["use_wake_word"]:
                if current_wake_word in transcript['text'].lower():
                    prompt = transcript['text'][transcript['text'].lower().index(current_wake_word) + len(current_wake_word):].strip()
                    print("Text after wake word:", prompt)
                    # holding_prompt += prompt
                    prompt_queue.put(prompt)
                elif override_wake_word is not None and override_wake_word in transcript['text'].lower():
                    prompt = transcript['text'][transcript['text'].lower().index(override_wake_word) + len(override_wake_word):].strip()
                    print("Text after override wake word:", prompt)
                    # holding_prompt += prompt
                    prompt_queue.put(prompt)
            elif transcript['text'] is not None and transcript['text'].strip() != "":
                print("No wake word detected, adding to holding prompt.")
                holding_prompt += transcript['text']                
        elif status == "partial":
            # Print the partial transcript for debugging purposes
            print("P:", transcript['partial'], end="\r")
            if transcript['partial'] is not None and transcript['partial'].strip() != "":                
                last_word_time = time()
            
        
        
        # print(f"Time since last word: {time() - last_word_time}")
        if time() - last_word_time > settings.config["silence_timeout"] and holding_prompt != "":
            print("Silence detected. Sending prompt to chatbot.")
            prompt_queue.put(holding_prompt)
            holding_prompt = ""
            
        if terminate_flag.is_set():
            break

async def handle_text_in():
    
    global current_conversation
    
    while True:
        user_query = input("You: ")  # Get user input
        user_query = user_query.strip()
        
        if user_query.lower() == "exit":  # Provide a way to exit the loop
            break
        else:
            await handle_input(user_query)


async def handle_voice_in():
    
    transcript_queue = queue.Queue()
    prompt_queue = queue.Queue()
        
    terminate_flag = threading.Event()
    listener_thread = threading.Thread(target=listener.run, args=(transcript_queue, terminate_flag))
    parser_thread = threading.Thread(
        target=transcript_parser_task, 
        args=(
            transcript_queue, 
            prompt_queue, 
            terminate_flag
    ))            
    listener_thread.start()
    parser_thread.start()
    
    try:
        while True:
            if prompt_queue.qsize() > 0:
                print("Prompt queue size:", prompt_queue.qsize())
                user_query:str = prompt_queue.get()
                user_query = user_query.strip()
                
                if user_query.lower() == "exit":  # Provide a way to exit the loop
                    print("Exiting...")
                    terminate_flag.set()
                    listener_thread.join()
                    parser_thread.join()
                    break
                else:  
                    await handle_input(user_query)
    finally:
        terminate_flag.set()
        listener_thread.join()
        parser_thread.join()


async def handle_input(user_query:str):
    
    global current_conversation
    chat_temperature = get_config()["chat_temperature"]
    
    if user_query.startswith("temp: "):
        chat_temperature = float(user_query.split(" ")[1])
        user_query = " ".join(str(item) for item in user_query.split(" ")[2:])
    
    if user_query.startswith("talk to "):
        character_name = user_query.split(" ")[2]
        switch_conversation(character_name)
        return
    elif user_query is None or user_query == "":
        return
    elif user_query == "clear":
        current_conversation.clear_conversation()
        return
    elif user_query == "load":
        load_name = input("Enter the name of the conversation to load: ")
        current_conversation.load_conversation(f"{load_name}.json")
        return
    elif user_query == "save":
        save_name = input("Enter a name for the conversation: ")
        current_conversation.save_conversation(f"{save_name}.json")
        return
    elif user_query == "undo":
        current_conversation.undo()
        return
    elif user_query.startswith("image"):
        if user_query.startswith("image_local"):
            url = images.get_base64_image_url(get_config()["local_image_name"])
        elif user_query.startswith("image: "):
            url = images.get_base64_image_url(user_query.split(" ")[1])
        elif user_query.startswith("image_url: "):
            url = user_query.split(" ")[1]
        else:
            print("Invalid image command. Please use 'image: ' or 'image_url: '")
            return
        content = [
            {"type": "text", "text": " ".join(str(item) for item in user_query.split(" ")[2:])},
            {"type": "image_url", "image_url": {"url": url}}
        ]
    else:
        content = user_query

    current_conversation.add_message('user', content)  # Append the user's message to the history
    
    await chat_completion(current_conversation, temperature=chat_temperature, logit_bias=get_bias())  # Await the chat completion and text-to-speech for the user's query


def switch_conversation(conversation_name):
    
    global current_conversation
    
    if conversation_name in conversations:
        print(f"Resuming conversation with {conversation_name}...")
        current_conversation = conversations[conversation_name]
    else:
        print(f"Starting conversation with {conversation_name}...")
        current_conversation = Conversation(conversation_name)
        conversations[conversation_name] = current_conversation
        
    current_conversation.activate()


async def main():
    
    global current_conversation
    mode = get_config()["chat_input_mode"]
    current_conversation = Conversation("assistant", voices["michael"])
    if mode == "text":
        await handle_text_in()
    elif mode == "voice":
        await handle_voice_in()


# Main execution
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
