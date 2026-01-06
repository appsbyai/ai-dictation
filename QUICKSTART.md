# Quick Start Guide

## Installation Steps

### 1. Run the installer
```bash
cd ~/ai-dictation
./install.sh
```

The installer will:
- Install system dependencies (wtype, portaudio, etc.)
- Set up Python virtual environment
- Install Python packages (evdev, sounddevice, faster-whisper, whispercpp)
- Download Whisper models (base model by default)
- Configure systemd user service
- Add you to the 'input' group
- Install udev rules for device permissions

### 2. **IMPORTANT: Log out and log back in**

This is required for the 'input' group membership to take effect.

### 3. Test the installation (optional but recommended)
```bash
cd ~/.local/share/ai-dictation
./venv/bin/python test_installation.py
```

This will verify:
- All Python modules are installed
- You're in the 'input' group
- wtype is available
- Audio input devices are detected
- Keyboard devices are accessible
- Whisper models are loaded

### 4. Enable and start the service
```bash
systemctl --user enable ai-dictation.service
systemctl --user start ai-dictation.service
```

### 5. Check the service status
```bash
systemctl --user status ai-dictation.service
```

You should see "Active: active (running)"

### 6. View logs (if needed)
```bash
journalctl --user -u ai-dictation.service -f
```

## Usage

1. **Press and hold Right Ctrl** - Recording starts
2. **Speak your text** - Keep Right Ctrl held down
3. **Release Right Ctrl** - Transcription happens, text is typed

The transcribed text will appear at your current cursor position in any application!

## Configuration

Edit the configuration file:
```bash
nano ~/.local/share/ai-dictation/config.py
```

Key settings:
- `WHISPER_BACKEND`: "whisper.cpp" or "faster-whisper"
- `WHISPER_MODEL`: "tiny", "base", "small", "medium", or "large"
- `WHISPER_LANGUAGE`: "en" or None for auto-detect
- `WHISPER_CPP_THREADS`: Number of CPU threads (default: 8)

After changing config:
```bash
systemctl --user restart ai-dictation.service
```

## Troubleshooting

### Service won't start
```bash
# Check logs
journalctl --user -u ai-dictation.service -n 50

# Try running manually
cd ~/.local/share/ai-dictation
./venv/bin/python dictation.py
```

### Permission denied errors
```bash
# Verify you're in input group
groups | grep input

# If not, add yourself and reboot
sudo usermod -a -G input $USER
# Then log out and log back in
```

### No audio input
```bash
# List audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

### wtype not working
```bash
# Install wtype
sudo apt install wtype

# Test it
wtype "Hello World"
```

## Performance Tips

- **For faster transcription**: Use "tiny" or "base" model
- **For better accuracy**: Use "small" or "medium" model
- **Adjust CPU threads**: Set `WHISPER_CPP_THREADS` to match your CPU core count
- **whisper.cpp vs faster-whisper**: whisper.cpp is generally faster on CPU

## Files and Directories

- **Installation**: `~/.local/share/ai-dictation/`
- **Configuration**: `~/.local/share/ai-dictation/config.py`
- **Service file**: `~/.config/systemd/user/ai-dictation.service`
- **Logs**: `journalctl --user -u ai-dictation.service`

## Uninstall

```bash
# Stop and disable service
systemctl --user stop ai-dictation.service
systemctl --user disable ai-dictation.service

# Remove files
rm -rf ~/.local/share/ai-dictation
rm -rf ~/.config/ai-dictation
rm ~/.config/systemd/user/ai-dictation.service

# Remove udev rule
sudo rm /etc/udev/rules.d/99-input-group.rules
sudo udevadm control --reload-rules

# Reload systemd
systemctl --user daemon-reload
```

## Next Steps

Enjoy your AI-powered dictation! Press Right Ctrl anywhere to start dictating.
