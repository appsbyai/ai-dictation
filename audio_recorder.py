"""
Audio recording module using sounddevice
"""

import io
import wave
import threading
import numpy as np
import sounddevice as sd
import logging
from config import SAMPLE_RATE, AUDIO_CHANNELS

logger = logging.getLogger('ai-dictation.audio')


class AudioRecorder:
    def __init__(self):
        """Initialize audio recorder"""
        self.sample_rate = SAMPLE_RATE
        self.channels = AUDIO_CHANNELS
        self.recording = False
        self.audio_data = []
        self.stream = None

        logger.info(f"Audio recorder initialized: {self.sample_rate}Hz, {self.channels} channel(s)")

    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream"""
        if status:
            logger.warning(f"Audio status: {status}")

        if self.recording:
            # Copy audio data
            self.audio_data.append(indata.copy())

    def start_recording(self):
        """Start recording audio"""
        if self.recording:
            logger.warning("Already recording!")
            return

        self.recording = True
        self.audio_data = []

        try:
            # Start input stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback,
                dtype=np.float32
            )
            self.stream.start()
            logger.info("Recording started")

        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.recording = False

    def stop_recording(self):
        """Stop recording and return audio data"""
        if not self.recording:
            logger.warning("Not currently recording!")
            return None

        self.recording = False

        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            # Concatenate all audio chunks
            if self.audio_data:
                audio_array = np.concatenate(self.audio_data, axis=0)

                # Flatten to 1D array (faster-whisper expects 1D, not 2D)
                audio_array = audio_array.flatten()

                logger.info(f"Recording stopped. Duration: {len(audio_array) / self.sample_rate:.2f}s")

                # Convert to bytes for Whisper
                # Whisper expects 16-bit PCM audio
                audio_int16 = (audio_array * 32767).astype(np.int16)

                return audio_int16
            else:
                logger.warning("No audio data recorded")
                return None

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return None

    def save_to_wav(self, audio_data, filename):
        """Save audio data to WAV file (for debugging)"""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            logger.info(f"Audio saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
