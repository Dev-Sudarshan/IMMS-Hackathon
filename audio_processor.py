import subprocess
import whisper
from config import FFMPEG_PATH

def transcribe_audio(video_path, audio_output):
    """Extract and transcribe audio from video"""
    try:
        ffmpeg_command = [
            FFMPEG_PATH, "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", audio_output
        ]
        
        result = subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return "[Error: Could not extract audio]"
        
        model = whisper.load_model("medium")
        result = model.transcribe(audio_output)
        return result["text"].strip()
    except Exception as e:
        return f"[Error transcribing audio: {str(e)}]"