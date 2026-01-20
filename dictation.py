#!/usr/bin/env python3
"""
AI Dictation System for Linux (Wayland)
Press and hold Right Ctrl to record voice, release to transcribe and type
"""

import os
import sys
import time
import threading
import queue
from pathlib import Path
import logging

import evdev
from evdev import InputDevice, categorize, ecodes

# Import config
from config import LOG_LEVEL

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai-dictation')


class DictationSystem:
    def __init__(self):
        self.recording = False
        self.audio_queue = queue.Queue()
        self.model = None
        self.audio_recorder = None

        # Import modules
        from audio_recorder import AudioRecorder
        from transcriber import Transcriber
        from text_injector import TextInjector

        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.text_injector = TextInjector()

        logger.info("Dictation system initialized")

    def find_keyboard_devices(self):
        """Find all input devices that have RIGHT_CTRL key"""
        keyboard_devices = []

        try:
            devices = [InputDevice(path) for path in evdev.list_devices()]

            for device in devices:
                caps = device.capabilities()
                if ecodes.EV_KEY in caps:
                    # Check if device has RIGHT_CTRL key
                    keys = caps[ecodes.EV_KEY]
                    if ecodes.KEY_RIGHTCTRL in keys:
                        # Skip virtual devices and security devices
                        device_name_lower = device.name.lower()
                        if ('virtual' in device_name_lower or
                            'yubikey' in device_name_lower or
                            'ydotoold' in device_name_lower):
                            logger.info(f"Skipping virtual/special device: {device.name} ({device.path})")
                            continue

                        keyboard_devices.append(device)
                        logger.info(f"Found keyboard: {device.name} ({device.path})")

            if not keyboard_devices:
                logger.error("No suitable keyboard devices found!")
                sys.exit(1)

        except Exception as e:
            logger.error(f"Error finding keyboard devices: {e}")
            sys.exit(1)

        return keyboard_devices

    def handle_key_event(self, event):
        """Handle key press/release events for RIGHT_CTRL"""
        if event.code == ecodes.KEY_RIGHTCTRL:
            if event.value == 1:  # Key press
                if not self.recording:
                    logger.info("RIGHT_CTRL pressed - starting recording")
                    self.start_recording()
            elif event.value == 0:  # Key release
                if self.recording:
                    logger.info("RIGHT_CTRL released - stopping recording")
                    self.stop_recording()

    def start_recording(self):
        """Start audio recording"""
        self.recording = True
        self.audio_recorder.start_recording()

    def stop_recording(self):
        """Stop recording and trigger transcription"""
        self.recording = False
        audio_data = self.audio_recorder.stop_recording()

        if audio_data is not None and len(audio_data) > 0:
            # Run transcription in a separate thread to avoid blocking
            threading.Thread(
                target=self.transcribe_and_type,
                args=(audio_data,),
                daemon=True
            ).start()

    def transcribe_and_type(self, audio_data):
        """Transcribe audio and type the result"""
        try:
            logger.info("Transcribing audio...")
            text = self.transcriber.transcribe(audio_data)

            if text and text.strip():
                logger.info(f"Transcribed: {text}")
                self.text_injector.type_text(text)
            else:
                logger.warning("No text transcribed")

        except Exception as e:
            logger.error(f"Error during transcription: {e}")

    def monitor_keyboard(self, device):
        """Monitor a single keyboard device"""
        logger.info(f"Monitoring {device.name}")

        try:
            # Don't grab the device - we want the keyboard to work normally
            # We'll just monitor for RIGHT_CTRL events
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    self.handle_key_event(event)

        except Exception as e:
            logger.error(f"Error monitoring {device.name}: {e}")

    def run(self):
        """Main run loop"""
        logger.info("Starting AI Dictation System...")
        logger.info("Press and hold RIGHT_CTRL to dictate")

        # Find all keyboard devices
        keyboards = self.find_keyboard_devices()

        # Start monitoring each keyboard in a separate thread
        threads = []
        for kbd in keyboards:
            thread = threading.Thread(
                target=self.monitor_keyboard,
                args=(kbd,),
                daemon=True
            )
            thread.start()
            threads.append(thread)

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            sys.exit(0)


def main():
    # Check if user is in input group
    import grp

    try:
        input_group = grp.getgrnam('input')
        user_groups = os.getgroups()

        if input_group.gr_gid not in user_groups:
            logger.error("User is not in 'input' group!")
            logger.error("Run: sudo usermod -a -G input $USER")
            logger.error("Then log out and log back in")
            sys.exit(1)
    except KeyError:
        logger.warning("Could not find 'input' group, proceeding anyway...")

    # Create and run the dictation system
    system = DictationSystem()
    system.run()


if __name__ == '__main__':
    main()
