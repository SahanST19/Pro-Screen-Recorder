from recorder import AudioRecorder
import time
import os

print("Initializing AudioRecorder...")
rec = AudioRecorder()
devices = rec.get_devices()
print("Available Devices:")
for d in devices:
    print(f"{d['index']}: {d['name']} ({d['rate']}Hz)")

if not devices:
    print("No devices found!")
    exit()

# Try recording from the first device (usually Microphone)
device_index = devices[0]['index'] # Use 0 or 1 depending on list
if len(devices) > 1:
     # Try to find a real microphone if possible, usually index 1
     device_index = devices[1]['index']

print(f"Recording from device index {device_index} for 3 seconds...")
rec.start(device_index, "test_audio_only.wav")
time.sleep(3)
rec.stop()

if os.path.exists("test_audio_only.wav"):
    size = os.path.getsize("test_audio_only.wav")
    print(f"Success! Audio file created. Size: {size} bytes")
else:
    print("Failure! Audio file not found.")
