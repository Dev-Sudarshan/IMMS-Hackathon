import os

# --- API Configuration ---
API_KEY = "9950e10d61694f288b5015e16c86112c"
DEPLOYMENT_URL = "https://api.turboline.ai/coreai/deployments/model-router/chat/completions?api-version=2025-01-01-preview"
HEADERS = {
    "Content-Type": "application/json",
    "tl-key": API_KEY
}

# --- FFMPEG Configuration ---
FFMPEG_PATH = r"D:\\ffmpeg-7.1.1-essentials_build\\bin\\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

# --- Frame Processing Configuration ---
DEFAULT_FPS = 1
DEFAULT_GROUP_SIZE = 5
DEFAULT_FRAME_INTERVAL = 30

# --- File Paths ---
FRAMES_FOLDER = "frames"
TEMP_AUDIO_FILE = "temp_audio.wav"

