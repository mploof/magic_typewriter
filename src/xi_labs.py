import requests
import json
import asyncio
import base64
import websockets
import yaml

import audio

voices = {
    "michael": "d5p9QsIisbcRbI3NQ5FR",
    "samantha": "bjehOvr3TnhggNkXv7bp",
    "sally": "09AoN6tYyW3VSTQqCo7C",
    "nina": "P2GZl52xQmbWlMkeefio",
    "tiffany": "x9leqCOAXOcmC5jtkq65",
    "ilya": "CnV6BQOHeZCIv4McSXDH",
    "cheryl": "wVZ5qbJFYF3snuC65nb4",
    "jennifer": "7NEwj4nuis0eiAI9AhKF"
}

with open("./config.yaml", 'r') as file:
    config = yaml.safe_load(file)

with open(f"./keys/{config['xi_key_file_name']}", "r") as f:
    XI_API_KEY = f.read().strip()

def get_voice_list():
    # This is the URL for the API endpoint we'll be making a GET request to.
    url = "https://api.elevenlabs.io/v1/voices"

    # Here, headers for the HTTP request are being set up. 
    # Headers provide metadata about the request. In this case, we're specifying the content type and including our API key for authentication.
    headers = {
    "Accept": "application/json",
    "xi-api-key": XI_API_KEY,
    "Content-Type": "application/json"
    }

    # A GET request is sent to the API endpoint. The URL and the headers are passed into the request.
    response = requests.get(url, headers=headers)

    # The JSON response from the API is parsed using the built-in .json() method from the 'requests' library. 
    # This transforms the JSON data into a Python dictionary for further processing.
    data = response.json()

    # A loop is created to iterate over each 'voice' in the 'voices' list from the parsed data. 
    # The 'voices' list consists of dictionaries, each representing a unique voice provided by the API.
    for voice in data['voices']:
        # For each 'voice', the 'name' and 'voice_id' are printed out. 
        # These keys in the voice dictionary contain values that provide information about the specific voice.
        print(f"{voice['name']}; {voice['voice_id']}")

def text_to_speech(
    text, 
    output_path="output.mp3", 
    voice_id=voices["michael"]
):
    # Define constants for the script
    CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
    VOICE_ID = voice_id  # ID of the voice model to use
    TEXT_TO_SPEAK = text  # Text you want to convert to speech
    OUTPUT_PATH = output_path  # Path to save the output audio file

    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    # Set up headers for the API request, including the API key for authentication
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": TEXT_TO_SPEAK,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    # Check if the request was successful
    if response.ok:
        # Open the output file in write-binary mode
        with open(OUTPUT_PATH, "wb") as f:
            # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        # Inform the user of success
        print("Audio stream saved successfully.")
    else:
        # Print the error message if the request was not successful
        print(response.text)


async def text_to_speech_input_streaming(
    text_iterator,
    text_chunker_fn,
    voice_id,
    stability=0.4,
    similarity_boost=0.9,
    style=0.0,
    use_speaker_boost=True
):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_monolingual_v1"

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({
                "text": " ",
                "voice_settings": 
                {
                    "stability":stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                },
                "xi_api_key": XI_API_KEY,
            }))

            async def listen():
                """Listen to the websocket for audio data and stream it."""
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        if data.get("audio"):
                            yield base64.b64decode(data["audio"])
                        elif data.get('isFinal'):
                            break
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed")
                        break

            listen_task = asyncio.create_task(audio.stream(listen()))

            async for text in text_chunker_fn(text_iterator):
                await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))

            await websocket.send(json.dumps({"text": ""}))

            await listen_task
    except asyncio.TimeoutError:
        print("Connection timed out.")

if __name__ == "__main__":
    get_voice_list()