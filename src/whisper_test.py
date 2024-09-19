###### Standard Imports ######
import yaml
import os

###### Third-Party Imports ######
from openai import OpenAI
import ffmpeg
from pydub import AudioSegment

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

def get_transcriptions(directory_path, language="en"):
    """
    Get transcriptions for all audio files in a directory.

    Args:
    - directory_path: The path to the directory containing the audio files.
    - language: The language of the audio files (default is English).
    """
    # Get a list of all files in the directory
    files = os.listdir(directory_path)
    
    # Rename .MP3 files to .mp3
    for file in files:
        if file.endswith(".MP3"):
            os.rename(os.path.join(directory_path, file), os.path.join(directory_path, file.replace(".MP3", ".mp3")))
    
    # Iterate over each file in the directory
    files = os.listdir(directory_path)
    for file in files:
        # Check if the file is an audio file
        if file.endswith(".mp3") or file.endswith(".opus"):
            # Get the full file path
            file_path = os.path.join(directory_path, file)

            # Get the transcription for the audio file
            get_transcription(file_path, language=language)

def get_transcription(file_path, is_segment=False, language="en"):
    
    file_name = os.path.basename(file_path)
    dir_name = os.path.dirname(file_path)
    
    # Check if the transcription already exists
    if file_name.replace(".opus", ".mp3") + ".txt" in os.listdir(dir_name):
        print(f"Transcription for {file_name} already exists.")
        return
        
    # Check if the file is an OPUS file and convert it to MP3 if necessary
    if file_name.endswith(".opus"):
        if not os.path.exists(file_path.replace(".opus", ".mp3")):
            convert_opus_to_mp3(file_path, file_path.replace(".opus", ".mp3"))
        file_path = file_path.replace(".opus", ".mp3")
    
    audio_file = open(file_path, "rb")
    
    # Get the size of the audio file in bytes
    file_size = os.path.getsize(file_path)
    
    if file_size > 20e6:
        base_file_name = file_name.replace(".mp3", "").replace(".MP3", "").replace(".opus", "")
        output_dir_name = os.path.join(dir_name, f"{base_file_name}_segments")
        
        if not os.path.exists(output_dir_name):
            split_mp3(file_path, 300, output_dir_name)
        
        for segment in os.listdir(output_dir_name):
            get_transcription(os.path.join(output_dir_name, segment), True)
        
        # Merge the transcriptions
        full_transcription = ""
        for file in os.listdir(output_dir_name):
            if file.endswith(".txt"):
                with open(os.path.join(output_dir_name, file), "r") as f:
                    full_transcription += f.read() + "\n"
                    
        with open(os.path.join(dir_name, f"{file_name}.txt"), "w") as f:
            f.write(full_transcription)
        
        # Delete the segments directory
        # for file in os.listdir(output_dir_name):
        #     os.remove(os.path.join(output_dir_name, file))
        # os.rmdir(output_dir_name)
                    
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
        response_format="text",
        language=language
    )
    print(transcription)
    with open(os.path.join(dir_name, f"{file_name}.txt"), "w", encoding="utf-8") as f:
        f.write(transcription)

def split_mp3(file_path, segment_duration_sec, output_dir):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(file_path)
    file_name = os.path.basename(file_path).replace(".mp3", "").replace(".MP3", "")

    # Calculate the length of the audio in milliseconds
    duration_ms = len(audio)

    # Convert segment duration from seconds to milliseconds
    segment_duration_ms = segment_duration_sec * 1000

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize segment counter
    segment_count = 1

    # Split the audio
    for i in range(0, duration_ms, segment_duration_ms):
        # Calculate end of segment
        segment_end = i + segment_duration_ms if i + segment_duration_ms < duration_ms else duration_ms

        # Extract the segment
        segment = audio[i:segment_end]

        # Generate segment filename
        
        segment_file_name = os.path.join(output_dir, f"{file_name}_{segment_count}.mp3")

        # Export segment
        segment.export(segment_file_name, format="mp3")
        
        # Increment the segment counter
        segment_count += 1

        # Print the segment file path
        print(f"Segment saved: {segment_file_name}")

        # Check if the audio segment reaches the end of the file
        if segment_end == duration_ms:
            break


get_transcriptions("F:\\Audio Recordings\\Alison")
