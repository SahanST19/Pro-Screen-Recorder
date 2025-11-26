from recorder import ScreenRecorder
import time
import os
import imageio_ffmpeg

print("Initializing ScreenRecorder...")
rec = ScreenRecorder()

# Get Audio Devices
devices = rec.get_audio_devices()
print("Available Audio Devices:")
for d in devices:
    print(f"{d['index']}: {d['name']} ({d['rate']}Hz)")

if not devices:
    print("No audio devices found! Cannot test audio.")
    exit()

# Use first device
audio_index = devices[0]['index']
if len(devices) > 1:
    audio_index = devices[1]['index']

print(f"Selected Audio Device Index: {audio_index}")

print("Starting recording (Video + Audio) for 5 seconds...")
rec.start_recording("test_full.mp4", fps=30, audio_device_index=audio_index)

time.sleep(5)

print("Stopping recording...")
rec.stop_recording()

print("Checking files...")
if os.path.exists("test_full.mp4"):
    size = os.path.getsize("test_full.mp4")
    print(f"Success! Output video exists. Size: {size} bytes")
else:
    print("Failure! Output video not found.")

if os.path.exists("temp_video.mp4"):
    print(f"Temp video still exists (size: {os.path.getsize('temp_video.mp4')}) - Muxing might have failed to clean up or was skipped.")
if os.path.exists("temp_audio.wav"):
    print(f"Temp audio still exists (size: {os.path.getsize('temp_audio.wav')})")

print(f"FFmpeg path: {imageio_ffmpeg.get_ffmpeg_exe()}")
