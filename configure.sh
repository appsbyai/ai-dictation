#!/bin/bash
# Quick launcher for the GTK Configuration Manager

# Check if we're in the right directory
if [ ! -f "config_manager.py" ]; then
    echo "Error: config_manager.py not found in current directory"
    echo "Make sure you're running this from the ai-dictation directory"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Try to import GTK
echo "Checking GTK dependencies..."
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk, Gdk, GLib" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "ERROR: Missing GTK dependencies!"
    echo ""
    echo "Please install the following packages:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    echo ""
    echo "Fedora:"
    echo "  sudo dnf install python3-gobject gtk3"
    echo ""
    echo "Arch Linux:"
    echo "  sudo pacman -S python-gobject gtk3"
    echo ""
    exit 1
fi

echo "Starting AI Dictation Configuration Manager..."
python3 config_manager.py
