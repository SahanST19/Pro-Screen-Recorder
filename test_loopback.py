import soundcard as sc
import numpy as np
import wave
import time

print("Scanning for microphones and loopback devices...")
mics = sc.all_microphones(include_loopback=True)

for i, mic in enumerate(mics):
    print(f"{i}: {mic.name} (Loopback: {mic.isloopback})")

# Try to find default speaker loopback
default_speaker = sc.default_speaker()
print(f"\nDefault Speaker: {default_speaker.name}")

# To record loopback, we need to find the microphone that corresponds to the speaker loopback
# soundcard usually exposes loopback devices in all_microphones(include_loopback=True)

loopback_mic = sc.get_microphone(id=str(default_speaker.id), include_loopback=True)
print(f"Loopback Mic for Default Speaker: {loopback_mic.name}")

print("Recording 3 seconds of system audio...")
data = loopback_mic.record(samplerate=44100, numframes=44100*3)

# Normalize and save
# data is float32 [-1, 1], shape (frames, channels)
print(f"Recorded data shape: {data.shape}")

# Convert to int16 for wav
data_int16 = (data * 32767).astype(np.int16)

with wave.open("test_loopback.wav", "wb") as wf:
    wf.setnchannels(data.shape[1])
    wf.setsampwidth(2) # 16 bit
    wf.setframerate(44100)
    wf.writeframes(data_int16.tobytes())

print("Saved test_loopback.wav")
