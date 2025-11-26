import customtkinter as ctk
import threading
import time
import os

from screeninfo import get_monitors
from recorder import ScreenRecorder

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ScreenRecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()


        self.title("Pro Screen Recorder")
        self.geometry("400x550")
        self.resizable(True, True)

        self.recorder = ScreenRecorder()
        self.is_recording = False
        self.start_time = 0

        self._setup_ui()

    def _setup_ui(self):
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Screen Recorder", 
            font=("Roboto Medium", 24)
        )
        self.title_label.pack(pady=20)

        # Status
        self.status_label = ctk.CTkLabel(
            self, 
            text="Ready", 
            text_color="gray",
            font=("Roboto", 14)
        )
        self.status_label.pack(pady=5)

        # Timer
        self.timer_label = ctk.CTkLabel(
            self, 
            text="00:00:00", 
            font=("Roboto Mono", 30)
        )
        self.timer_label.pack(pady=10)

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=20, padx=20, fill="x")

        self.fps_label = ctk.CTkLabel(self.settings_frame, text="FPS:")
        self.fps_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.fps_option = ctk.CTkOptionMenu(
            self.settings_frame, 
            values=["30", "60"]
        )
        self.fps_option.set("60")
        self.fps_option.grid(row=0, column=1, padx=10, pady=10)



        self.filename_entry = ctk.CTkEntry(
            self.settings_frame, 
            placeholder_text="Filename (e.g. video.mp4)"
        )
        self.filename_entry.insert(0, "recording.mp4")
        self.filename_entry.grid(row=0, column=2, padx=(10, 5), pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(
            self.settings_frame,
            text="...",
            width=30,
            command=self.browse_file
        )
        self.browse_button.grid(row=0, column=3, padx=(0, 10), pady=10)

        # Monitor Selection

        # Monitor Selection
        self.monitors = self.recorder.get_monitors()
        self.monitor_values = []
        
        # Get real monitor names using screeninfo
        try:
            real_monitors = get_monitors()
        except:
            real_monitors = []

        for i, m in enumerate(self.monitors):
            if i == 0:
                name = "All Monitors"
            else:
                # Try to find matching real monitor
                # mss index 1 matches real_monitors[0] usually
                name = f"Monitor {i}"
                if i <= len(real_monitors):
                     # Simple mapping attempt
                     try:
                         name = real_monitors[i-1].name.replace("\\.\\", "")
                     except:
                         pass
            
            self.monitor_values.append(f"{name} ({m['width']}x{m['height']})")

        self.monitor_label = ctk.CTkLabel(self.settings_frame, text="Screen:")
        self.monitor_label.grid(row=1, column=0, padx=10, pady=10)

        self.monitor_option = ctk.CTkOptionMenu(
            self.settings_frame,
            values=self.monitor_values
        )
        # Default to Monitor 1 if available, else All Monitors
        if len(self.monitor_values) > 1:
            self.monitor_option.set(self.monitor_values[1])
        else:
            self.monitor_option.set(self.monitor_values[0])
            
        self.monitor_option.grid(row=1, column=1, padx=10, pady=10, columnspan=2, sticky="ew")

        # Cursor Checkbox
        self.cursor_var = ctk.BooleanVar(value=False)
        self.cursor_checkbox = ctk.CTkCheckBox(
            self.settings_frame,
            text="Record Cursor",
            variable=self.cursor_var
        )
        self.cursor_checkbox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Audio Selection
        self.audio_devices = self.recorder.get_audio_devices()
        self.audio_values = ["No Audio"]
        for dev in self.audio_devices:
            name = dev['name']
            if dev['is_loopback']:
                name += " (Loopback)"
            self.audio_values.append(name)

        self.audio_label = ctk.CTkLabel(self.settings_frame, text="Audio:")
        self.audio_label.grid(row=3, column=0, padx=10, pady=10)

        self.audio_option = ctk.CTkOptionMenu(
            self.settings_frame,
            values=self.audio_values
        )
        self.audio_option.set("No Audio")
        self.audio_option.grid(row=3, column=1, padx=10, pady=10, columnspan=2, sticky="ew")

        # Buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=20)

        self.start_button = ctk.CTkButton(
            self.button_frame, 
            text="Start Recording", 
            command=self.start_recording,
            fg_color="#2CC985",
            hover_color="#229965",
            width=150,
            height=40,
            font=("Roboto Medium", 14)
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ctk.CTkButton(
            self.button_frame, 
            text="Stop", 
            command=self.stop_recording,
            fg_color="#FF4B4B",
            hover_color="#CC3C3C",
            state="disabled",
            width=100,
            height=40,
            font=("Roboto Medium", 14)
        )
        self.stop_button.grid(row=0, column=1, padx=10)

        # Developer Credit
        self.credit_label = ctk.CTkLabel(
            self,
            text="Developed by Sahan Tharuka",
            font=("Roboto", 10),
            text_color="gray"
        )
        self.credit_label.pack(side="bottom", pady=10)

    def start_recording(self):
        fps = int(self.fps_option.get())
        filename = self.filename_entry.get()
        if not filename.endswith(".mp4"):
            filename += ".mp4"





        # Find selected monitor index
        selected_str = self.monitor_option.get()
        monitor_index = self.monitor_values.index(selected_str)
        record_cursor = self.cursor_var.get()

        # Find selected monitor index
        selected_str = self.monitor_option.get()
        monitor_index = self.monitor_values.index(selected_str)
        record_cursor = self.cursor_var.get()

        # Find selected audio device
        audio_str = self.audio_option.get()
        audio_device_id = None
        if audio_str != "No Audio":
            # Remove " (Loopback)" suffix if present for matching
            clean_name = audio_str.replace(" (Loopback)", "")
            for dev in self.audio_devices:
                # We match by name and loopback status if possible, or just ID
                # Construct the display name again to match exactly
                dev_display_name = dev['name']
                if dev['is_loopback']:
                    dev_display_name += " (Loopback)"
                
                if dev_display_name == audio_str:
                    audio_device_id = dev['id']
                    break

        self.recorder.start_recording(
            filename=filename, 
            fps=fps, 
            monitor_index=monitor_index, 
            record_cursor=record_cursor,
            audio_device_id=audio_device_id
        )
        self.is_recording = True
        self.start_time = time.time()
        
        self.status_label.configure(text="Recording...", text_color="#FF4B4B")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.fps_option.configure(state="disabled")


        self.filename_entry.configure(state="disabled")
        self.monitor_option.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.cursor_checkbox.configure(state="disabled")
        self.audio_option.configure(state="disabled")

        self._update_timer()

    def stop_recording(self):
        self.recorder.stop_recording()
        self.is_recording = False
        
        self.status_label.configure(text="Saved to " + self.recorder.output_filename, text_color="#2CC985")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.fps_option.configure(state="normal")


        self.filename_entry.configure(state="normal")
        self.monitor_option.configure(state="normal")
        self.browse_button.configure(state="normal")
        self.cursor_checkbox.configure(state="normal")
        self.audio_option.configure(state="normal")

    def _update_timer(self):
        if self.is_recording:
            elapsed = int(time.time() - self.start_time)
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            s = elapsed % 60
            self.timer_label.configure(text=f"{h:02}:{m:02}:{s:02}")
            self.after(1000, self._update_timer)

    def browse_file(self):
        filename = ctk.filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")]
        )
        if filename:
            self.filename_entry.delete(0, "end")
            self.filename_entry.insert(0, filename)

if __name__ == "__main__":
    app = ScreenRecorderApp()
    app.mainloop()
