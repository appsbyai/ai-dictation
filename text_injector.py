"""
Text injection module using DIRECT ydotool typing (no clipboard)
This is your original working method - reinstated
"""

import subprocess
import time
import logging
from config import (
    TYPE_DELAY_MS,
    AUTO_CAPITALIZE,
    AUTO_PUNCTUATE,
    ADD_SPACE_BEFORE
)

logger = logging.getLogger('ai-dictation.text_injector')


class TextInjector:
    def __init__(self):
        """Initialize text injector"""
        self.delay_ms = TYPE_DELAY_MS
        logger.info("Text injector initialized (direct ydotool typing)")

    def type_text(self, text):
        """
        Type text directly using ydotool (your original working method)
        
        Args:
            text: Text string to type
        """
        if not text:
            logger.warning("No text to type")
            return

        try:
            # Small delay to ensure the application has focus
            if self.delay_ms > 0:
                time.sleep(self.delay_ms / 1000.0)

            # Use ydotool to type the text directly
            # Add delay between keystrokes to prevent dropped characters
            # --key-delay: delay between keystrokes (ms)
            subprocess.run(
                ['ydotool', 'type', '--key-delay', '12', text],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            logger.info(f"Typed {len(text)} characters successfully")

        except FileNotFoundError:
            logger.error("ydotool not found! Please install: sudo apt install ydotool")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout typing text (text too long?)")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error typing text with ydotool: {e}")
            if e.stderr:
                logger.error(f"stderr: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error typing text: {e}")

    def type_with_formatting(self, text):
        """
        Type text with automatic capitalization and punctuation

        Args:
            text: Raw transcribed text
        """
        # Clean up the text
        text = text.strip()

        if not text:
            return

        # Capitalize first letter
        if AUTO_CAPITALIZE and text and text[0].islower():
            text = text[0].upper() + text[1:]

        # Add period if no ending punctuation
        if AUTO_PUNCTUATE and text and text[-1] not in '.!?':
            text += '.'

        # Add space before typing (unless we're at the start of a line)
        if ADD_SPACE_BEFORE:
            text = ' ' + text

        self.type_text(text)