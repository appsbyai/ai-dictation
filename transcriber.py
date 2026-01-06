"""
Transcription module supporting whisper.cpp and faster-whisper
"""

import numpy as np
import logging
from config import (
    WHISPER_BACKEND,
    WHISPER_MODEL,
    WHISPER_LANGUAGE,
    WHISPER_CPP_THREADS,
    USE_VAD,
    VAD_THRESHOLD,
    USE_GPU,
    GPU_COMPUTE_TYPE
)

logger = logging.getLogger('ai-dictation.transcriber')


class Transcriber:
    def __init__(self):
        """Initialize Whisper transcriber based on configured backend"""
        self.backend = WHISPER_BACKEND
        self.model_size = WHISPER_MODEL
        self.language = WHISPER_LANGUAGE
        self.model = None

        logger.info(f"Initializing {self.backend} with model: {self.model_size}")

        if self.backend == "whisper.cpp":
            self._load_whisper_cpp()
        elif self.backend == "faster-whisper":
            self._load_faster_whisper()
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _load_whisper_cpp(self):
        """Load whisper.cpp model"""
        try:
            from whispercpp import Whisper

            # Model file path (downloaded by installer)
            model_path = f"models/ggml-{self.model_size}.bin"

            self.model = Whisper.from_pretrained(
                self.model_size,
                basedir="models"
            )

            logger.info(f"whisper.cpp model loaded: {model_path}")

        except Exception as e:
            logger.error(f"Error loading whisper.cpp model: {e}")
            logger.info("Falling back to faster-whisper...")
            self.backend = "faster-whisper"
            self._load_faster_whisper()

    def _load_faster_whisper(self):
        """Load faster-whisper model (fallback)"""
        try:
            from faster_whisper import WhisperModel

            # Determine device and compute type
            device = "cuda" if USE_GPU else "cpu"
            compute_type = GPU_COMPUTE_TYPE if USE_GPU else "int8"

            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
                num_workers=4
            )

            logger.info(f"faster-whisper model loaded on {device} with {compute_type} precision")

        except Exception as e:
            logger.error(f"Error loading faster-whisper model: {e}")
            # Try falling back to CPU if GPU fails
            if USE_GPU:
                logger.warning("GPU failed, falling back to CPU...")
                try:
                    self.model = WhisperModel(
                        self.model_size,
                        device="cpu",
                        compute_type="int8",
                        num_workers=4
                    )
                    logger.info("faster-whisper model loaded on CPU (fallback)")
                except Exception as e2:
                    logger.error(f"CPU fallback also failed: {e2}")
                    raise
            else:
                raise

    def transcribe(self, audio_data):
        """
        Transcribe audio data to text

        Args:
            audio_data: numpy array of audio samples (int16)

        Returns:
            Transcribed text string
        """
        if self.model is None:
            logger.error("Model not loaded!")
            return ""

        try:
            # Convert int16 to float32 normalized to [-1, 1]
            audio_float32 = audio_data.astype(np.float32) / 32768.0

            if self.backend == "whisper.cpp":
                return self._transcribe_whisper_cpp(audio_float32)
            else:
                return self._transcribe_faster_whisper(audio_float32)

        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return ""

    def _transcribe_whisper_cpp(self, audio_float32):
        """Transcribe using whisper.cpp"""
        try:
            # whisper.cpp expects float32 audio
            result = self.model.transcribe(
                audio_float32,
                language=self.language if self.language else None,
                n_threads=WHISPER_CPP_THREADS
            )

            # Extract text from result
            if isinstance(result, dict):
                text = result.get('text', '').strip()
            elif isinstance(result, str):
                text = result.strip()
            else:
                # Result is likely an iterator
                text = ' '.join([segment['text'].strip() for segment in result]).strip()

            logger.info(f"whisper.cpp transcribed: {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Error in whisper.cpp transcription: {e}")
            return ""

    def _transcribe_faster_whisper(self, audio_float32):
        """Transcribe using faster-whisper"""
        try:
            segments, info = self.model.transcribe(
                audio_float32,
                beam_size=5,
                language=self.language if self.language else None,
                vad_filter=USE_VAD,
                vad_parameters={
                    "threshold": VAD_THRESHOLD,
                    "min_speech_duration_ms": 250,
                    "min_silence_duration_ms": 100
                } if USE_VAD else None
            )

            # Combine all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            full_text = " ".join(text_parts).strip()

            logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            logger.info(f"faster-whisper transcribed: {len(full_text)} characters")

            return full_text

        except Exception as e:
            logger.error(f"Error in faster-whisper transcription: {e}")
            return ""
