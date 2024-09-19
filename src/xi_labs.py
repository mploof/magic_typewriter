import requests
import json
import asyncio
import base64
import websockets
import yaml
import uuid
from enum import Enum
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

import audio
import settings
from settings import get_config

voices = {
    "michael": "d5p9QsIisbcRbI3NQ5FR",
    "samantha": "bjehOvr3TnhggNkXv7bp",
    "sally": "09AoN6tYyW3VSTQqCo7C",
    "nina": "P2GZl52xQmbWlMkeefio",
    "tiffany": "x9leqCOAXOcmC5jtkq65",
    "ilya": "CnV6BQOHeZCIv4McSXDH",
    "cheryl": "wVZ5qbJFYF3snuC65nb4",
    "jennifer": "7NEwj4nuis0eiAI9AhKF",
    "elizabeth": "LGGSADQ2UFf7xNvljNZp",
    "amy": "2bk7ULW9HfwvcIbMWod0",
}

client = ElevenLabs(
    api_key=settings.XI_LABS_API_KEY
)


def get_voice_list():
    # This is the URL for the API endpoint we'll be making a GET request to.
    url = "https://api.elevenlabs.io/v1/voices"

    # Here, headers for the HTTP request are being set up. 
    # Headers provide metadata about the request. In this case, we're specifying the content type and including our API key for authentication.
    headers = {
    "Accept": "application/json",
    "xi-api-key": settings.XI_LABS_API_KEY,
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

def text_to_speech(text: str, voice_id=voices['michael']) -> str:
    """
    Converts text to speech and saves the output as an MP3 file.

    This function uses a specific client for text-to-speech conversion. It configures
    various parameters for the voice output and saves the resulting audio stream to an
    MP3 file with a unique name.

    Args:
        text (str): The text content to convert to speech.

    Returns:
        str: The file path where the audio file has been saved.
    """
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id=voice_id,
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=get_config()["stability"],
            similarity_boost=get_config()["similarity_boost"],
            style=get_config()["style"],
            use_speaker_boost=get_config()["use_speaker_boost"],
        ),
    )

    # Generating a unique file name for the output MP3 file
    save_file_path = f"output.mp3"
    # Writing the audio stream to the file

    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"A new audio file was saved successfully at {save_file_path}")

    # Return the path of the saved audio file
    return save_file_path

def text_to_speech_stream(
    text, 
    output_path="output_stream.mp3", 
    voice_id=voices["michael"],
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
        "xi-api-key": settings.XI_LABS_API_KEY
    }

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": TEXT_TO_SPEAK,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": get_config()["stability"],
            "similarity_boost": get_config()["similarity_boost"],
            "style": get_config()["style"],
            "use_speaker_boost": get_config()["use_speaker_boost"]
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
        print(f"Error: {response.text}")


async def text_stream_to_speech_stream(
    text_iterator,
    text_chunker_fn,
    voice_id,
    stability=get_config()["stability"],
    similarity_boost=get_config()["similarity_boost"],
    style=get_config()["style"],
    use_speaker_boost=get_config()["use_speaker_boost"],
    break_phrases=[]
):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_monolingual_v1"
    print(f"Voice ID: {voice_id}")
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
                "xi_api_key": settings.XI_LABS_API_KEY,
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

            full_response = ""
            
            class BreakType(Enum):
                NONE = 0
                DELAYED = 1
                IMMEDIATE = 2

            break_flag = BreakType.NONE
            async for text in text_chunker_fn(text_iterator):
                full_response += text
                
                # Check if the text contains any break phrases
                for phrase in break_phrases:
                    if phrase in text:
                        phase_index = text.find(phrase)
                        # Only send text prior to the break phrase
                        if phase_index != -1:
                            break_flag = BreakType.DELAYED
                            text = text[:phase_index]
                            print("*** Split break phrase, halting speech generation now. ***\n\n")
                        else:
                            # If the break phrase is not found, it means the break phrase is split
                            # between the previous chunk and the current chunk, so we ignore the 
                            # rest of the text in the current chunk
                            break_flag = BreakType.IMMEDIATE
                            print("*** Full break phrase found, finishing up speech generation. ***\n\n")

                print(text, end="")
                
                if break_flag != BreakType.IMMEDIATE:
                    await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))
                    
                
                if break_flag == BreakType.DELAYED:
                    break_flag = BreakType.IMMEDIATE
                    

            # Send an empty text to signal the end of the stream
            await websocket.send(json.dumps({"text": ""}))
            print("\n\n")

            await listen_task
    except asyncio.TimeoutError:
        print("Connection timed out.")

if __name__ == "__main__":
    get_voice_list()
    text_to_speech_stream("This is a test.")
    text_to_speech("This is a test.")