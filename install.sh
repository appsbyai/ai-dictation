#!/bin/bash
# AI Dictation System Installer for Ubuntu/Wayland
# This script installs all dependencies and sets up the systemd service

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="$HOME/.local/share/ai-dictation"
CONFIG_DIR="$HOME/.config/ai-dictation"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AI Dictation System Installer${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running on Wayland
if [ "$XDG_SESSION_TYPE" != "wayland" ]; then
    echo -e "${YELLOW}Warning: Not running on Wayland. This system is designed for Wayland.${NC}"
    echo -e "${YELLOW}XDG_SESSION_TYPE=$XDG_SESSION_TYPE${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root!${NC}"
    echo -e "${YELLOW}Run it as your regular user. It will ask for sudo when needed.${NC}"
    exit 1
fi

echo -e "${GREEN}[1/6] Installing system dependencies...${NC}"

# Update package list
sudo apt update

# Install required system packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    wtype \
    portaudio19-dev \
    python3-dev \
    build-essential \
    libportaudio2 \
    libportaudiocpp0

echo -e "${GREEN}[2/6] Creating installation directory...${NC}"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

# Copy Python files
cp dictation.py "$INSTALL_DIR/"
cp audio_recorder.py "$INSTALL_DIR/"
cp transcriber.py "$INSTALL_DIR/"
cp text_injector.py "$INSTALL_DIR/"
cp config.py "$INSTALL_DIR/"

echo -e "${GREEN}[3/6] Setting up Python virtual environment...${NC}"

# Create virtual environment
python3 -m venv "$INSTALL_DIR/venv"

# Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Upgrade pip
pip install --upgrade pip

echo -e "${GREEN}[4/6] Installing Python dependencies...${NC}"

# Install Python packages
pip install \
    evdev \
    numpy \
    sounddevice \
    faster-whisper \
    whispercpp

echo -e "${GREEN}[5/6] Downloading Whisper models...${NC}"

# Create models directory
mkdir -p "$INSTALL_DIR/models"

# Pre-download whisper.cpp model
echo -e "${YELLOW}Downloading whisper.cpp 'base' model...${NC}"
python3 << 'EOFDL'
from whispercpp import Whisper
import os

# Change to the installation directory
os.chdir(os.path.expanduser("~/.local/share/ai-dictation"))

print("Downloading whisper.cpp 'base' model...")
try:
    model = Whisper.from_pretrained("base", basedir="models")
    print("whisper.cpp model downloaded successfully!")
except Exception as e:
    print(f"Error downloading whisper.cpp model: {e}")
    print("Will try to download faster-whisper as fallback...")
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("faster-whisper model downloaded successfully!")
EOFDL

echo -e "${GREEN}[6/6] Setting up systemd service...${NC}"

# Create systemd service file
SERVICE_FILE="$HOME/.config/systemd/user/ai-dictation.service"
mkdir -p "$HOME/.config/systemd/user"

cat > "$SERVICE_FILE" << EOFSERVICE
[Unit]
Description=AI Dictation System
After=graphical-session.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/dictation.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Environment
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=default.target
EOFSERVICE

echo -e "${GREEN}Service file created at: $SERVICE_FILE${NC}"

# Add user to input group for device access
echo -e "${GREEN}Adding user to 'input' group for keyboard access...${NC}"
sudo usermod -a -G input "$USER"

# Install udev rule for input device permissions
echo -e "${GREEN}Installing udev rule for input device permissions...${NC}"
sudo cp 99-input-group.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT: You need to log out and log back in for group changes to take effect!${NC}"
echo ""
echo -e "Installation directory: ${GREEN}$INSTALL_DIR${NC}"
echo -e "Service file: ${GREEN}$SERVICE_FILE${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo -e "  1. Log out and log back in (for input group membership)"
echo -e "  2. Enable the service: ${YELLOW}systemctl --user enable ai-dictation.service${NC}"
echo -e "  3. Start the service: ${YELLOW}systemctl --user start ai-dictation.service${NC}"
echo -e "  4. Check status: ${YELLOW}systemctl --user status ai-dictation.service${NC}"
echo -e "  5. View logs: ${YELLOW}journalctl --user -u ai-dictation.service -f${NC}"
echo ""
echo -e "${GREEN}Usage:${NC}"
echo -e "  - Press and hold ${YELLOW}Right Ctrl${NC} to start recording"
echo -e "  - Speak your text"
echo -e "  - Release ${YELLOW}Right Ctrl${NC} to transcribe and type"
echo ""
echo -e "${GREEN}To test without installing service (after logging back in):${NC}"
echo -e "  ${YELLOW}cd $INSTALL_DIR && ./venv/bin/python dictation.py${NC}"
echo ""
