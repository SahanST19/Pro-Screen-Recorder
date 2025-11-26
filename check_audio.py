import pyaudio

p = pyaudio.PyAudio()
print("Scanning audio devices...")
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

found_input = False
for i in range(0, numdevices):
    dev_info = p.get_device_info_by_host_api_device_index(0, i)
    if dev_info.get('maxInputChannels') > 0:
        found_input = True
        print(f"Device {i}: {dev_info.get('name')}")
        print(f"  Max Input Channels: {dev_info.get('maxInputChannels')}")
        print(f"  Default Sample Rate: {dev_info.get('defaultSampleRate')}")

if not found_input:
    print("No input devices found!")

p.terminate()
