import subprocess
import asyncio

from scipy.io.wavfile import write
import numpy as np
import sounddevice as sd

import yaml

with open("config.yaml", 'r') as file:
    config = yaml.safe_load(file)

# Global or shared state to control recording
is_recording = False
recording_buffer = []

############################################
# RECORDING FUNCTIONS
############################################

async def capture(seconds, output_path):
    fs = 44100  # Sample rate

    print("Starting recording...")
    recording = await asyncio.to_thread(sd.rec, int(seconds * fs), samplerate=fs, channels=2, blocking=True)
    sd.wait()  # Wait for the recording to finish in the separate thread
    print("Recording finished.")
    write(output_path, fs, recording)  # Save as WAV file

# Global or shared state to control recording
is_recording = False
recording_buffer = []

async def start_recording(fs=44100, channels=2):
    global is_recording
    global recording_buffer
    
    def callback(indata, frames, time, status):
        """This callback is called for each audio block from the input device."""
        recording_buffer.extend(indata.copy())

    print("Starting recording...")
    is_recording = True
    recording_buffer = []
    stream = sd.InputStream(samplerate=fs, channels=channels, callback=callback)
    with stream:
        while is_recording:
            await asyncio.sleep(0.1)  # Sleep briefly to yield control
    print("Recording stopped.")


async def stop_recording(output_path, fs=44100):
    global is_recording
    global recording_buffer
    
    is_recording = False
    await asyncio.sleep(0.2)  # Wait a bit for the recording loop to finish
    
    if recording_buffer:
        # Convert buffer to numpy array and write to WAV file
        recording = np.array(recording_buffer)
        write(output_path, fs, recording)
        print(f"Recording saved to {output_path}.")
    else:
        print("Recording was empty.")


############################################
# PLAYBACK FUNCTIONS
############################################

async def stream(audio_stream):
    # TODO: Fix installation check
    # """Stream audio data using mpv player."""
    # if not is_installed("mpv"):
    #     raise ValueError(
    #         "mpv not found, necessary to stream audio. "
    #         "Install instructions: https://mpv.io/installation/"
    #     )

    mpv_process = subprocess.Popen(
        [config["mpv_path"], "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    print("Started streaming audio")
    async for chunk in audio_stream:
        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()
    

async def play_file(file_path):
    # Use the full path to the mpv executable if it's not in your system's PATH environment variable
    mpv_executable = config["mpv_path"]

    # Start mpv to play the specified audio file
    mpv_process = subprocess.Popen(
        [mpv_executable, "--no-cache", "--no-terminal", file_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    print(f"Started playing {file_path}")

    # Wait for mpv to finish playing the file
    await asyncio.to_thread(mpv_process.wait)
    print(f"Finished playing {file_path}")


############################################
# MAIN FUNCTIONS
############################################

async def console_input():
    while True:
        user_input = input("Enter 'q' to quit: ")
        if user_input.lower() == 'q':
            raise asyncio.CancelledError # Cancel the main task

async def main():
    pass

if __name__ == "__main__":
    pass
