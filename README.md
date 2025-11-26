# 🎥 Pro Screen Recorder

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/Media-FFmpeg-red?style=for-the-badge&logo=ffmpeg)

A modern, high-performance Screen and Audio recorder built with Python. This application allows you to record your screen with system audio or microphone input, featuring a clean dark-mode UI.

![App Screenshot](screenshot.png)
## 🚀 Features

* **🖥️ Multi-Monitor Support:** Automatically detects and lets you choose which screen to record.
* **🔊 System Audio Recording:** Capable of recording internal system sounds (Loopback) or Microphone input.
* **🎨 Modern UI:** Built with `CustomTkinter` for a sleek, dark-themed user interface.
* **🖱️ Cursor Capture:** Toggle whether to record the mouse cursor or not.
* **⚡ High Performance:** Uses `MSS` for fast screen capture and `FFmpeg` for efficient video encoding.
* **⚙️ Customizable:** Adjustable Frame Rate (30/60 FPS) and custom output filenames.

## 🛠️ Technologies Used

* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):** For the modern GUI.
* **[MSS](https://python-mss.readthedocs.io/):** Ultra-fast cross-platform screen shot module.
* **[SoundCard](https://github.com/bastibe/SoundCard):** For capturing system audio and microphone input.
* **[ImageIO & FFmpeg](https://imageio.readthedocs.io/):** For processing video frames and mixing audio/video.
* **[NumPy](https://numpy.org/):** For efficient array manipulations.

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/SahanST19/Pro-Screen-Recorder.git](https://github.com/SahanST19/Pro-Screen-Recorder.git)
    cd Pro-Screen-Recorder
    ```

2.  **Install Dependencies**
    Make sure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

    *Note: FFmpeg is required. The `imageio[ffmpeg]` package usually handles this, but ensure you have it set up if issues arise.*

## ▶️ Usage

Run the main application file:

```bash
python main.py