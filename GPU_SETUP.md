# GPU Acceleration Setup for AI Dictation

## Overview
GPU acceleration can significantly speed up transcription times (3-5x faster) but requires proper NVIDIA driver and cuDNN installation.

## Current Status: CPU Mode (Default)
The system is configured to run in CPU mode by default for maximum compatibility.

```python
# config.py
USE_GPU = False  # CPU mode - works on all systems
```

## Requirements for GPU Mode

### 1. NVIDIA GPU with CUDA Support
- NVIDIA GPU with Compute Capability 6.0 or higher
- Check: https://developer.nvidia.com/cuda-gpus

### 2. NVIDIA Driver
```bash
# Check if NVIDIA driver is installed
nvidia-smi

# If not installed, install via:
sudo apt update
sudo apt install nvidia-driver-535  # Or latest version
```

### 3. CUDA Toolkit
```bash
# Check CUDA version
nvcc --version

# Install CUDA (if not present)
sudo apt install nvidia-cuda-toolkit
```

### 4. cuDNN Library (CRITICAL)

**Option A: Install via Package Manager (Recommended)**
```bash
# Add NVIDIA package repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install cuDNN
sudo apt-get install libcudnn8 libcudnn8-dev

# Verify installation
ldconfig -p | grep cudnn
```

**Option B: Manual Download from NVIDIA**
1. Register at https://developer.nvidia.com/cudnn
2. Download cuDNN for your CUDA version
3. Extract and copy files:
```bash
tar -xvf cudnn-linux-x86_64-8.x.x.x_cudaX.Y-archive.tar.xz
sudo cp cuda/lib64/libcudnn* /usr/lib/x86_64-linux-gnu/
sudo cp cuda/include/cudnn*.h /usr/include/
sudo chmod a+r /usr/lib/x86_64-linux-gnu/libcudnn*
```

## Testing cuDNN Installation

```bash
# Should show libcudnn libraries
ldconfig -p | grep cudnn

# Expected output:
# libcudnn.so.8 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libcudnn.so.8
# libcudnn_ops_infer.so.8 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libcudnn_ops_infer.so.8

# Check specific library needed by faster-whisper
ls /usr/lib/x86_64-linux-gnu/libcudnn_ops.so.8
```

## Enabling GPU Mode

Once cuDNN is properly installed:

1. **Edit config.py:**
```bash
nano ~/.local/share/ai-dictation/config.py
```

2. **Change GPU setting:**
```python
USE_GPU = True  # Enable GPU acceleration
GPU_COMPUTE_TYPE = "float16"  # Options: "float16", "int8_float16", "int8"
```

3. **Restart service:**
```bash
systemctl --user restart ai-dictation.service
```

4. **Verify GPU is used:**
```bash
journalctl --user -u ai-dictation.service -n 20 | grep "model loaded"
# Should show: "faster-whisper model loaded on cuda with float16 precision"
```

## Troubleshooting

### "Unable to load libcudnn_ops.so"
**Cause:** cuDNN not installed or not in library path
**Solution:** Install cuDNN following steps above

### "CUDA out of memory"
**Cause:** GPU memory insufficient for model
**Solution:** Use smaller model (base, small instead of medium/large)

### Service crashes during transcription
**Cause:** CUDA/cuDNN version mismatch
**Solution:** Ensure cuDNN version matches CUDA version
```bash
# Check versions
nvidia-smi  # Shows CUDA version
apt list --installed | grep cudnn  # Shows cuDNN version
```

## Performance Comparison

| Model | CPU (int8) | GPU (float16) | Speedup |
|-------|-----------|---------------|---------|
| tiny  | 32x RT    | 100x RT       | 3.1x    |
| base  | 16x RT    | 50x RT        | 3.1x    |
| small | 8x RT     | 25x RT        | 3.1x    |
| medium| 4x RT     | 12x RT        | 3.0x    |
| large | 2x RT     | 6x RT         | 3.0x    |

*RT = Real-time (e.g., 16x RT means transcribes 16 seconds of audio in 1 second)*

## Alternative: Use Google Colab
If local GPU setup is problematic, consider running on Google Colab with free GPU access.
