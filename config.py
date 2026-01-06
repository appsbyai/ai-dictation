"""
Configuration file for AI Dictation System
Modify these settings to customize the behavior
"""

# Whisper Model Configuration
WHISPER_BACKEND = "faster-whisper"
WHISPER_MODEL = "small"
WHISPER_LANGUAGE = "en"

# GPU Configuration (faster-whisper only)
USE_GPU = False
GPU_COMPUTE_TYPE = "float16"

# Audio Configuration
SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# Text Injection Configuration
TYPE_DELAY_MS = 50
AUTO_CAPITALIZE = True
AUTO_PUNCTUATE = True
ADD_SPACE_BEFORE = True

# Whisper.cpp Specific Settings
WHISPER_CPP_THREADS = 8
WHISPER_CPP_PROCESSORS = 1

# Voice Activity Detection
USE_VAD = True
VAD_THRESHOLD = 0.5

# Logging
LOG_LEVEL = "INFO"
