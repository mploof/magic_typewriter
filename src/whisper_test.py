###### Standard Imports ######
import yaml
import os

###### Third-Party Imports ######
from openai import OpenAI
import ffmpeg

###### Local Imports ######

###### Global Vars ######
with open("./config.yaml", 'r') as file:
    config = yaml.safe_load(file)

with open(f"./keys/{config['gpt_key_file_name']}", "r") as f:
    OPENAI_API_KEY = f.read().strip()
    
client = OpenAI(api_key=OPENAI_API_KEY)

def convert_opus_to_mp3(opus_file_path, mp3_file_path):
    """
    Convert an OPUS file to MP3 format using ffmpeg-python.

    Args:
    - opus_file_path: The file path of the source OPUS file.
    - mp3_file_path: The desired file path for the output MP3 file.
    """
    try:
        # Convert OPUS to MP3
        stream = ffmpeg.input(opus_file_path)
        ffmpeg.output(stream, mp3_file_path, format='mp3').run()
        print(f"Conversion successful! MP3 file saved as: {mp3_file_path}")
    except ffmpeg.Error as e:
        print(f"An error occurred during conversion: {e}")

def get_transcription(file_name):
    path = f"./data/{file_name}"
    if file_name.endswith(".opus"):
        if not os.path.exists(path.replace(".opus", ".mp3")):
            convert_opus_to_mp3(path, path.replace(".opus", ".mp3"))
        path = path.replace(".opus", ".mp3")
    audio_file = open(path, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file, 
    response_format="text"
    )
    print(transcription)
    with open(f"./data/{file_name}.txt", "w") as f:
        f.write(transcription)

get_transcription("wa2.opus")
