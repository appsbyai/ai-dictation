#!/usr/bin/env python3
"""
Test script to verify AI Dictation installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing module imports...")

    modules = [
        ('evdev', 'evdev'),
        ('numpy', 'numpy'),
        ('sounddevice', 'sounddevice'),
        ('faster-whisper', 'faster_whisper'),
        ('whispercpp', 'whispercpp'),
    ]

    all_ok = True
    for name, module in modules:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            all_ok = False

    return all_ok


def test_input_group():
    """Test if user is in input group"""
    print("\nTesting input group membership...")

    import grp

    try:
        input_group = grp.getgrnam('input')
        user_groups = os.getgroups()

        if input_group.gr_gid in user_groups:
            print("  ✓ User is in 'input' group")
            return True
        else:
            print("  ✗ User is NOT in 'input' group")
            print("    Run: sudo usermod -a -G input $USER")
            print("    Then log out and log back in")
            return False
    except KeyError:
        print("  ⚠ Could not find 'input' group")
        return False


def test_wtype():
    """Test if wtype is installed"""
    print("\nTesting wtype installation...")

    import subprocess

    try:
        result = subprocess.run(
            ['wtype', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        print(f"  ✓ wtype is installed: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("  ✗ wtype not found")
        print("    Run: sudo apt install wtype")
        return False
    except Exception as e:
        print(f"  ✗ Error testing wtype: {e}")
        return False


def test_audio_devices():
    """Test if audio input devices are available"""
    print("\nTesting audio devices...")

    try:
        import sounddevice as sd

        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]

        if input_devices:
            print(f"  ✓ Found {len(input_devices)} input device(s)")
            for i, dev in enumerate(input_devices[:3]):  # Show first 3
                print(f"    - {dev['name']}")
            return True
        else:
            print("  ✗ No audio input devices found")
            return False

    except Exception as e:
        print(f"  ✗ Error checking audio devices: {e}")
        return False


def test_keyboard_devices():
    """Test if keyboard devices are accessible"""
    print("\nTesting keyboard device access...")

    try:
        import evdev
        from evdev import ecodes

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        keyboards = []

        for device in devices:
            caps = device.capabilities()
            if ecodes.EV_KEY in caps:
                keys = caps[ecodes.EV_KEY]
                if ecodes.KEY_RIGHTCTRL in keys:
                    if 'yubikey' not in device.name.lower():
                        keyboards.append(device)

        if keyboards:
            print(f"  ✓ Found {len(keyboards)} keyboard device(s) with RIGHT_CTRL")
            for kbd in keyboards:
                print(f"    - {kbd.name}")
            return True
        else:
            print("  ✗ No suitable keyboard devices found")
            return False

    except PermissionError:
        print("  ✗ Permission denied accessing keyboard devices")
        print("    Make sure you're in the 'input' group and have logged out/in")
        return False
    except Exception as e:
        print(f"  ✗ Error checking keyboard devices: {e}")
        return False


def test_whisper_models():
    """Test if Whisper models are available"""
    print("\nTesting Whisper models...")

    try:
        # Try whisper.cpp first
        try:
            from whispercpp import Whisper
            model = Whisper.from_pretrained("base", basedir="models")
            print("  ✓ whisper.cpp 'base' model loaded")
            return True
        except Exception as e:
            print(f"  ⚠ whisper.cpp model failed: {e}")

        # Fall back to faster-whisper
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("base", device="cpu", compute_type="int8")
            print("  ✓ faster-whisper 'base' model loaded")
            return True
        except Exception as e:
            print(f"  ✗ faster-whisper model failed: {e}")
            return False

    except Exception as e:
        print(f"  ✗ Error loading Whisper models: {e}")
        return False


def main():
    print("=" * 60)
    print("AI Dictation System - Installation Test")
    print("=" * 60)
    print()

    tests = [
        ("Module Imports", test_imports),
        ("Input Group", test_input_group),
        ("wtype Installation", test_wtype),
        ("Audio Devices", test_audio_devices),
        ("Keyboard Devices", test_keyboard_devices),
        ("Whisper Models", test_whisper_models),
    ]

    results = {}
    for name, test_func in tests:
        results[name] = test_func()

    # Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print()
        print("🎉 All tests passed! Your installation looks good.")
        print()
        print("Next steps:")
        print("  1. Enable service: systemctl --user enable ai-dictation.service")
        print("  2. Start service: systemctl --user start ai-dictation.service")
        print("  3. Check status: systemctl --user status ai-dictation.service")
        print()
        return 0
    else:
        print()
        print("⚠ Some tests failed. Please fix the issues above before proceeding.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
