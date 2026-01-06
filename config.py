"""
Configuration file for AI Dictation System
Modify these settings to customize the behavior
"""

# Whisper Model Configuration
WHISPER_BACKEND = "faster-whisper"  # Options: "whisper.cpp" or "faster-whisper"
WHISPER_MODEL = "medium"  # Options: tiny, base, small, medium, large, large-v3, turbo
WHISPER_LANGUAGE = ""  # Language code (en, es, fr, de, etc.) or None for auto-detect

# GPU Configuration (faster-whisper only)
USE_GPU = False  # Enable GPU acceleration (requires CUDA + cuDNN)
GPU_COMPUTE_TYPE = "float16"  # Options: "float16" (fastest), "int8_float16" (lower memory), "int8"

# Audio Configuration
SAMPLE_RATE = 16000  # 16kHz is optimal for Whisper
AUDIO_CHANNELS = 1  # Mono audio

# Text Injection Configuration
TYPE_DELAY_MS = 50  # Delay before typing (milliseconds)
AUTO_CAPITALIZE = True  # Automatically capitalize first letter
AUTO_PUNCTUATE = True  # Automatically add period if missing
ADD_SPACE_BEFORE = True  # Add space before typed text

# Whisper.cpp Specific Settings
WHISPER_CPP_THREADS = 8  # Number of CPU threads (adjust for your CPU)
WHISPER_CPP_PROCESSORS = 1  # Number of processors to use

# Voice Activity Detection
USE_VAD = True  # Enable voice activity detection to filter silence
VAD_THRESHOLD = 0.5  # Voice activity threshold (0.0 - 1.0)

# Logging
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
