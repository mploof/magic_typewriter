import asyncio
import json
from openai import AsyncOpenAI
import threading
import queue
import yaml

import xi_labs
from xi_labs import voices

import listener

with open("config.yaml", 'r') as file:
    config = yaml.safe_load(file)
    
VOICE_ID = voices[config["default_voice"]]
    
with open(f"./keys/{config['gpt_key_file_name']}", "r") as f:
    OPENAI_API_KEY = f.read().strip()

# Set OpenAI API key
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def printer(queue: asyncio.Queue):
    """A coroutine that prints messages from a queue."""
    while True:
        message = await queue.get()
        if message is None:  # Sentinel value to break the loop
            break
        print(message, end="", flush=True)


async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if text is None:  # Skip None values
            continue
        elif buffer.endswith(splitters):
            yield buffer + " "
            buffer = text
        elif text.startswith(splitters):
            yield buffer + text[0] + " "
            buffer = text[1:]
        else:
            buffer += text

    if buffer:
        yield buffer + " "



async def chat_completion(messages, print_queue):
    """Retrieve text from OpenAI using the conversation history and pass it to the text-to-speech function."""
    response = await aclient.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=1,
        stream=True
    )

    async def text_iterator():
        this_message = ""
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                await print_queue.put(delta.content)  # Enqueue the text for printing
                this_message += " " + delta.content
            yield delta.content
        messages.append({'role': 'assistant', 'content': this_message})  # Update conversation history
        await print_queue.put(None)  # Signal to the printer coroutine that we're done

    await xi_labs.text_to_speech_input_streaming(text_iterator(), VOICE_ID)

def transcript_parser(transcript_queue, prompt_queue, terminate_flag, wake_word_queue):
    current_wake_word = "computer"
    while True:
        if not wake_word_queue.empty():
            current_wake_word = wake_word_queue.get()  # Update the wake word
        transcript, status = transcript_queue.get()
        transcript = json.loads(transcript)
        if status == "final":
            print("F:", transcript['text'])
            if current_wake_word in transcript['text'].lower():
                prompt = transcript['text'][transcript['text'].lower().index(current_wake_word) + len(current_wake_word):].strip()
                print("Text after wake word:", prompt)
                prompt_queue.put(prompt)
        elif status == "partial":
            print("P:", transcript['partial'], end="\r")
        if terminate_flag.is_set():
            break

async def main():
    print_queue = asyncio.Queue()
    wake_word_queue = queue.Queue()  # Queue for sharing the wake word
    messages = []  # This will keep track of the conversation history
    mode = "voice"
    context_dir = "contexts"
    
    with open(f"./{context_dir}/initial_context.txt", "r") as f:
        initial_context = f.read().strip()
    
    try:
        messages.append({'role': 'user', 'content': initial_context})
        if mode == "text":
            while True:
                user_query = input("You: ")  # Get user input
                user_query = user_query.strip()
                messages.append({'role': 'user', 'content': user_query})  # Append the user's message to the history
                if user_query.lower() == "exit":  # Provide a way to exit the loop
                    break
                if user_query is None or user_query == "":
                    continue
                await chat_completion(messages, print_queue)  # Await the chat completion and text-to-speech for the user's query
        elif mode == "voice":
            transcript_queue = queue.Queue()
            prompt_queue = queue.Queue()
            terminate_flag = threading.Event()
            
            listener_thread = threading.Thread(target=listener.run, args=(transcript_queue, terminate_flag))
            parser_thread = threading.Thread(target=transcript_parser, args=(transcript_queue, prompt_queue, terminate_flag, wake_word_queue))            
            listener_thread.start()
            parser_thread.start()
            while True:
                if prompt_queue.qsize() > 0:
                    print("Prompt queue size:", prompt_queue.qsize())
                    user_query = prompt_queue.get()
                    user_query = user_query.strip()
                    
                    if user_query.lower() == "exit":  # Provide a way to exit the loop
                        print("Exiting...")
                        await print_queue.put(None)  # Signal to the printer coroutine that we're done
                        terminate_flag.set()
                        listener_thread.join()
                        parser_thread.join()
                        break
                    elif user_query == "undo":
                        messages.pop()
                        messages.pop()
                        continue
                    elif user_query.startswith("voice"):
                        voice = user_query.split(" ")[1]
                        if voice == "jesse":
                            voice = "jessi"
                        try:
                            global VOICE_ID
                            VOICE_ID = voices[voice]
                            wake_word_queue.put(voice)
                            try:
                                with open(f"./{context_dir}/{voice}_context.txt", "r") as f:
                                    messages = [{'role': 'user', 'content': f.read().strip()}]
                            except FileNotFoundError:
                                messages = [{'role': 'user', 'content': initial_context}]
                            print("Voice set to", voice)
                        except KeyError:
                            print("Voice not found.")
                            print("Available voices:", list(voices.keys()))
                        continue
                    elif user_query is None or user_query == "":
                        continue
                    else:
                        # Append the user's message to the history
                        user_query += f" (Limit your output to {config['max_words']} words or less if I have not already prompted you otherwise)"
                        messages.append({'role': 'user', 'content': user_query})
                        print(messages)
                        # Await the chat completion and text-to-speech for the user's query
                        await chat_completion(messages, print_queue)

        # Wait for the printer task to complete before exiting
        print("Printing final messages...")
        await asyncio.create_task(printer(print_queue))
    finally:
        print("Exiting...")
        if mode == "voice":
            terminate_flag.set()
            listener_thread.join()
            parser_thread.join()
        print("Printing final messages...")
        await print_queue.put(None)
        await asyncio.create_task(printer(print_queue))



# Main execution
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

