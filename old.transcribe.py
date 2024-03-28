import subprocess, sys, os, json
import pprint

from datetime import datetime, timedelta

from vosk import Model, KaldiRecognizer, SetLogLevel
import soundfile as sf

import sounddevice as sd
import numpy as np

from scipy.io.wavfile import write
import os

SetLogLevel(-1)

class Transcriber():
    def __init__(self, model_path):
        self.model = Model(model_path)

    def fmt(self, data):
        data = json.loads(data)

        start = min(r["start"] for r in data.get("result", [{ "start": 0 }]))
        end = max(r["end"] for r in data.get("result", [{ "end": 0 }]))

        return {
            "start": str(timedelta(seconds=start)), 
            "end": str(timedelta(seconds=end)), 
            "text": data["text"]
        }

    def transcribe(self, filename):
        _, sample_rate = sf.read(filename)
        rec = KaldiRecognizer(self.model, sample_rate)
        rec.SetWords(True)

        if not os.path.exists(filename):
            raise FileNotFoundError(filename)

        transcription = []

        ffmpeg_command = [
                "ffmpeg",
                "-nostdin",
                "-loglevel",
                "quiet",
                "-i",
                filename,
                "-ar",
                str(sample_rate),
                "-ac",
                "1",
                "-f",
                "s16le",
                "-",
            ]

        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE) as process:

            start_time = datetime.now() 
            while True:
                data = process.stdout.read(4000)
                if len(data) == 0:
                    break
                
                if rec.AcceptWaveform(data):
                    transcription.append(self.fmt(rec.Result()))

            transcription.append(self.fmt(rec.FinalResult()))
            end_time = datetime.now()

            time_elapsed = end_time - start_time
            print(f"Time elapsed  {time_elapsed}")

        return {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "elapsed_time": time_elapsed,
            "transcription": transcription,
        }

class StreamingTranscriber:
    def __init__(self, model_path, wake_word):
        self.model = Model(model_path)
        self.wake_word = wake_word.lower()
        self.file_count = 0
        self.directory = "recordings"
        self.fs = 44100
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        
    def callback(self, indata, frames, time, status):
        
        # filename = os.path.join(self.directory, f"recording_{self.file_count}.wav")
        # write(filename, self.fs, indata)  # Save the block of audio data to a WAV file
        # self.file_count += 1
        # print(f"Saved {filename}")
                
        """This callback is called for each audio chunk from the microphone."""
        # Ensure indata is treated as a numpy array and convert to bytes
        audio_bytes = np.asarray(indata, dtype=np.int16).tobytes()
        
        if self.rec.AcceptWaveform(indata):
            result = json.loads(self.rec.Result())
            text = result.get('text', '').lower()
            print(f"Partial transcription: {text}")
            if self.wake_word in text:
                print(f"Wake word detected: {text}")
                # Handle wake word detection event here

    def listen(self, sample_rate=44100):
        self.rec = KaldiRecognizer(self.model, sample_rate)
        self.rec.SetWords(True)

        with sd.InputStream(samplerate=sample_rate, blocksize=44100, dtype='int16', channels=1, callback=self.callback):
            print("Listening for wake word...")
            sd.sleep(-1)  # Listen indefinitely


def transcribe(filename):
    model_path = "vosk-model-small-en-us-0.15"

    transcriber = Transcriber(model_path)
    transcription = transcriber.transcribe(filename)

    return transcription

# if __name__ == "__main__":
#     filename = "example_speech.wav"
#     transcription = transcribe(filename)
#     pprint.pprint(transcription)
    
#     for s in transcription["transcription"]:
#         print(s["text"])
        
if __name__ == "__main__":
    model_path = "vosk-model-small-en-us-0.15"
    wake_word = "hello"  # Specify the wake word you're listening for

    transcriber = StreamingTranscriber(model_path, wake_word)
    transcriber.listen()
