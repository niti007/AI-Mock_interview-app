import os
import uuid
import wave
import contextlib
import subprocess
from typing import Tuple
import whisper


class AudioHandler:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.whisper_model = whisper.load_model("base")

    def record_audio(self, filename: str = None) -> Tuple[str, float]:
        """
        Record audio from the user's default microphone.

        Args:
            filename (str, optional): Filename for the recorded audio. If not provided, a unique filename will be generated.

        Returns:
            Tuple[str, float]: The recorded audio filename and duration in seconds.
        """
        if not filename:
            filename = f"{uuid.uuid4().hex}.wav"
        audio_path = os.path.join(self.data_dir, filename)

        # Use ffmpeg to record audio from the default input device
        subprocess.run(["ffmpeg", "-f", "alsa", "-i", "default", "-t", "60", "-y", audio_path], check=True)

        # Get the duration of the recorded audio
        with contextlib.closing(wave.open(audio_path, 'r')) as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = frames / float(rate)

        return audio_path, duration

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe the given audio file using the Whisper speech recognition model.

        Args:
            audio_path (str): Path to the audio file to be transcribed.

        Returns:
            str: The transcribed text.
        """
        result = self.whisper_model.transcribe(audio_path)
        return result["text"]