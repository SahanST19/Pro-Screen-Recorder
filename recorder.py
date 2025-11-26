import mss
import numpy as np
import imageio
import imageio_ffmpeg
import threading
import time
import platform
import ctypes
import queue
import soundcard as sc
import wave
import os
import subprocess
from PIL import Image, ImageDraw
from screeninfo import get_monitors

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.thread = None
        self.mic = None
        self.output_filename = "temp_audio.wav"
        self.sample_rate = 44100

    def get_devices(self):
        devices = []
        try:
            # Get all microphones including loopback
            mics = sc.all_microphones(include_loopback=True)
            for i, mic in enumerate(mics):
                devices.append({
                    "id": mic.id,
                    "name": mic.name,
                    "is_loopback": mic.isloopback
                })
        except Exception as e:
            print(f"Error getting audio devices: {e}")
        return devices

    def start(self, device_id, filename="temp_audio.wav"):
        self.output_filename = filename
        self.is_recording = True
        
        # Find mic by ID
        mics = sc.all_microphones(include_loopback=True)
        self.mic = None
        for m in mics:
            if m.id == device_id:
                self.mic = m
                break
        
        if not self.mic:
            print(f"Audio device {device_id} not found!")
            return

        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def stop(self):
        self.is_recording = False
        if self.thread:
            self.thread.join()

    def _record(self):
        try:
            print(f"Recording audio from: {self.mic.name}")
            with self.mic.recorder(samplerate=self.sample_rate) as recorder:
                all_data = []
                while self.is_recording:
                    # Record in small chunks
                    data = recorder.record(numframes=1024)
                    all_data.append(data)
                
                # Save after recording stops
                if all_data:
                    full_data = np.concatenate(all_data)
                    # Normalize and convert to int16
                    data_int16 = (full_data * 32767).astype(np.int16)
                    
                    with wave.open(self.output_filename, "wb") as wf:
                        wf.setnchannels(full_data.shape[1])
                        wf.setsampwidth(2) # 16 bit
                        wf.setframerate(self.sample_rate)
                        wf.writeframes(data_int16.tobytes())
                        
        except Exception as e:
            print(f"Audio recording error: {e}")

class ScreenRecorder:
    def __init__(self):
        self.is_recording = False
        self.output_filename = "output.mp4"
        self.fps = 60
        self.monitor_index = 1
        self.record_cursor = False
        self.audio_recorder = AudioRecorder()
        
        self._stop_event = threading.Event()
        self.capture_thread = None
        self.write_thread = None
        self.frame_queue = queue.Queue()
        self.start_time = 0

    def get_monitors(self):
        with mss.mss() as sct:
            return sct.monitors

    def get_audio_devices(self):
        return self.audio_recorder.get_devices()

    def start_recording(self, filename="output.mp4", fps=60, monitor_index=1, record_cursor=False, audio_device_id=None):
        if self.is_recording:
            return

        self.output_filename = filename
        self.fps = fps
        self.monitor_index = monitor_index
        self.record_cursor = record_cursor
        self.is_recording = True
        self._stop_event.clear()
        
        # Clear queue
        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()

        # Start Audio
        self.audio_enabled = audio_device_id is not None
        if self.audio_enabled:
            self.audio_recorder.start(audio_device_id, "temp_audio.wav")

        self.start_time = time.time()

        # Start Threads
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.write_thread = threading.Thread(target=self._write_loop)
        
        self.capture_thread.start()
        self.write_thread.start()

    def stop_recording(self):
        if not self.is_recording:
            return
            
        self.is_recording = False
        self._stop_event.set()
        
        if self.audio_enabled:
            self.audio_recorder.stop()

        if self.capture_thread:
            self.capture_thread.join()
        if self.write_thread:
            self.write_thread.join()

        if self.audio_enabled:
            self._mux_audio_video()
            # Cleanup temp files
            if os.path.exists("temp_video.mp4"):
                try: os.remove("temp_video.mp4")
                except: pass
            if os.path.exists("temp_audio.wav"):
                try: os.remove("temp_audio.wav")
                except: pass

    def _capture_loop(self):
        with mss.mss() as sct:
            if self.monitor_index >= len(sct.monitors):
                self.monitor_index = 1
            monitor = sct.monitors[self.monitor_index]
            
            while not self._stop_event.is_set():
                try:
                    capture_time = time.time()
                    img = sct.grab(monitor)
                    frame = np.array(img)
                    
                    if self.record_cursor:
                        self._draw_cursor_on_frame(frame, monitor)

                    # Convert BGRA to RGB
                    frame = frame[:, :, :3]
                    frame = frame[:, :, ::-1]

                    self.frame_queue.put((frame, capture_time))
                    time.sleep(0.001) 
                except Exception as e:
                    print(f"Capture error: {e}")

            self.frame_queue.put(None)

    def _write_loop(self):
        target_file = "temp_video.mp4" if self.audio_enabled else self.output_filename
        
        writer = imageio.get_writer(
            target_file, 
            fps=self.fps, 
            codec='libx264', 
            quality=None, 
            pixelformat='yuv420p',
            macro_block_size=16,
            ffmpeg_params=['-preset', 'ultrafast', '-crf', '23']
        )

        frame_duration = 1.0 / self.fps
        video_time_covered = 0.0
        first_frame_time = None

        while True:
            item = self.frame_queue.get()
            if item is None:
                break
            
            frame, capture_time = item
            
            if first_frame_time is None:
                first_frame_time = capture_time
            
            elapsed_real_time = capture_time - first_frame_time
            
            while video_time_covered < elapsed_real_time:
                writer.append_data(frame)
                video_time_covered += frame_duration
            
            self.frame_queue.task_done()
        
        writer.close()

    def _draw_cursor_on_frame(self, frame, monitor):
        try:
            cursor_pos = self._get_cursor_pos()
            rel_x = cursor_pos[0] - monitor["left"]
            rel_y = cursor_pos[1] - monitor["top"]
            
            if 0 <= rel_x < monitor["width"] and 0 <= rel_y < monitor["height"]:
                radius = 5
                pil_img = Image.fromarray(frame)
                draw = ImageDraw.Draw(pil_img)
                draw.ellipse((rel_x - radius, rel_y - radius, rel_x + radius, rel_y + radius), fill='red', outline='white')
                np.copyto(frame, np.array(pil_img))
        except:
            pass

    def _get_cursor_pos(self):
        point = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        return (point.x, point.y)

    def _mux_audio_video(self):
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"Muxing using ffmpeg at: {ffmpeg_exe}")
        
        if os.path.exists("temp_video.mp4"):
            print(f"Temp video size: {os.path.getsize('temp_video.mp4')} bytes")
        
        if os.path.exists("temp_audio.wav"):
            print(f"Temp audio size: {os.path.getsize('temp_audio.wav')} bytes")

        cmd = [
            ffmpeg_exe,
            "-y",
            "-i", "temp_video.mp4",
            "-i", "temp_audio.wav",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest", 
            self.output_filename
        ]
        
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr}")
            else:
                print("Muxing successful.")
        except Exception as e:
            print(f"Muxing exception: {e}")
