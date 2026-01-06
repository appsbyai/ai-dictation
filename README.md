# AI Dictation System for Linux (Wayland)

A system-wide voice dictation system for Linux that works anywhere. Press and hold **Right Ctrl** to record your voice, release to transcribe with Whisper AI, and automatically type the result at your cursor position.

## Features

- 🎤 **System-wide dictation**: Works in any application
- ⌨️ **Simple trigger**: Press and hold Right Ctrl
- 🚀 **Local processing**: All transcription happens on your machine (no internet required)
- 🔒 **Privacy-focused**: No data sent to external servers
- ⚡ **Fast**: Uses faster-whisper for efficient CPU transcription
- 🖥️ **Wayland native**: Built for modern Linux desktop environments
- ⚙️ **GTK Configuration Manager**: Easy GUI for managing settings and service control

## System Requirements

- **OS**: Ubuntu 25.10 (or similar modern Linux distribution)
- **Display Server**: Wayland
- **Desktop**: GNOME 49 or compatible
- **CPU**: Modern multi-core CPU (i7-14700KF or similar recommended)
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: ~500MB for models and dependencies

## Architecture

- **whisper.cpp**: Ultra-fast C++ implementation of OpenAI Whisper (with faster-whisper as fallback)
- **evdev**: Low-level keyboard monitoring
- **sounddevice**: Audio capture
- **wtype**: Wayland text injection
- **systemd**: Service management

## Installation

1. Clone or download this repository
2. Navigate to the directory:
   ```bash
   cd ai-dictation
   ```

3. Run the installer:
   ```bash
   ./install.sh
   ```

4. **Important**: Log out and log back in (for input group membership)

5. Enable and start the service:
   ```bash
   systemctl --user enable ai-dictation.service
   systemctl --user start ai-dictation.service
   ```

## Usage

1. **Start dictating**: Press and hold **Right Ctrl**
2. **Speak**: Say what you want to type
3. **Release**: Let go of **Right Ctrl** to transcribe and type

The transcribed text will appear at your current cursor position.

## Configuration

You can configure AI Dictation using the **GTK Configuration Manager** (GUI) or by editing the configuration file directly.

### Using the GTK Configuration Manager

Launch the graphical configuration tool:
```bash
./config_manager.py
```

The configuration manager provides:
- **Visual interface** for all settings with tooltips and validation
- **Service control** - Start, stop, restart, and view logs
- **Real-time previews** of model sizes and performance impacts
- **Safe editing** with error checking and backups

### Manual Configuration

All configuration is stored in `$HOME/.local/share/ai-dictation/config.py`:

```python
# Whisper Backend
WHISPER_BACKEND = "whisper.cpp"  # Options: "whisper.cpp" or "faster-whisper"
WHISPER_MODEL = "base"           # Options: tiny, base, small, medium, large
WHISPER_LANGUAGE = "en"          # Language code or None for auto-detect

# Audio
SAMPLE_RATE = 16000              # 16kHz optimal for Whisper
AUDIO_CHANNELS = 1               # Mono audio

# Text Injection
TYPE_DELAY_MS = 50               # Delay before typing
AUTO_CAPITALIZE = True           # Auto-capitalize first letter
AUTO_PUNCTUATE = True            # Auto-add period if missing
ADD_SPACE_BEFORE = True          # Add space before text

# Performance (whisper.cpp)
WHISPER_CPP_THREADS = 8          # CPU threads (adjust for your CPU)
```

### Model Size Comparison

- **tiny**: ~75MB, fastest, least accurate (~32x real-time on CPU)
- **base**: ~145MB, good balance (default) (~16x real-time on CPU)
- **small**: ~466MB, better accuracy (~8x real-time on CPU)
- **medium**: ~1.5GB, high accuracy (~4x real-time on CPU)
- **large**: ~3GB, best accuracy (~2x real-time on CPU)

### Backend Comparison

- **whisper.cpp**: Faster, lower memory, C++ implementation (recommended for CPU)
- **faster-whisper**: Good balance, Python-friendly, automatic fallback

After changing configuration, restart the service:
```bash
systemctl --user restart ai-dictation.service
```

## Troubleshooting

### Check service status
```bash
systemctl --user status ai-dictation.service
```

### View logs
```bash
journalctl --user -u ai-dictation.service -f
```

### Test manually (without service)
```bash
cd ~/.local/share/ai-dictation
./venv/bin/python dictation.py
```

### Permission issues
Make sure you're in the `input` group:
```bash
groups | grep input
```

If not, run:
```bash
sudo usermod -a -G input $USER
```
Then log out and log back in.

### wtype not found
```bash
sudo apt install wtype
```

### No audio device
Check your audio input:
```bash
pactl list sources short
```

## Uninstallation

```bash
# Stop and disable service
systemctl --user stop ai-dictation.service
systemctl --user disable ai-dictation.service

# Remove files
rm -rf ~/.local/share/ai-dictation
rm -rf ~/.config/ai-dictation
rm ~/.config/systemd/user/ai-dictation.service

# Reload systemd
systemctl --user daemon-reload
```

## Performance Tips

- **Model size**: Start with `base`, upgrade to `small` if you need better accuracy
- **CPU threads**: The system automatically uses multiple CPU threads for faster transcription
- **RAM**: Larger models require more RAM (base ~1GB, large ~3GB)

## Known Limitations

- Only works on Wayland (not X11)
- Right Ctrl key is exclusively captured when held
- Initial transcription may take a few seconds
- Background noise can affect accuracy

## License

MIT License - Feel free to modify and distribute

## Credits

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Efficient Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [wtype](https://github.com/atx/wtype) - Wayland typing tool
