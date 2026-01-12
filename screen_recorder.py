import cv2
import numpy as np
import pyautogui
import datetime
import os
import threading
import queue

try:
    import sounddevice as sd
    import wave
except ImportError:
    sd = None
    wave = None

try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    try:
        # Fallback for older moviepy versions
        from moviepy.editor import VideoFileClip, AudioFileClip
    except ImportError:
        VideoFileClip = None
        AudioFileClip = None


def ensure_output_dir(path: str = "recordings") -> str:
    """Create output directory if it does not exist and return the path."""
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def record_audio(stop_event: threading.Event, audio_path: str, samplerate: int = 44100, channels: int = None):
    """
    Record microphone audio to a .wav file until stop_event is set.
    Requires the 'sounddevice' package: pip install sounddevice
    """
    if sd is None or wave is None:
        print("Audio recording is not available because 'sounddevice' is not installed.")
        print("Install it with: pip install sounddevice")
        return

    # Detect available channels from default input device
    if channels is None:
        try:
            device_info = sd.query_devices(kind='input')
            channels = device_info['max_input_channels']
            # Use mono (1) if device supports it, otherwise use what's available
            if channels > 1:
                channels = 1  # Most microphones are mono
            print(f"Using {channels} channel(s) for audio recording")
        except Exception as e:
            print(f"Warning: Could not detect audio device channels, using mono: {e}")
            channels = 1

    q: "queue.Queue[np.ndarray]" = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        q.put(indata.copy())

    try:
        with wave.open(audio_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(samplerate)

            with sd.InputStream(samplerate=samplerate, channels=channels, dtype="int16", callback=callback):
                print(f"Audio recording started... Audio will be saved as {audio_path}")
                while not stop_event.is_set():
                    try:
                        data = q.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    wf.writeframes(data.tobytes())
    except sd.PortAudioError as e:
        print(f"Error starting audio recording: {e}")
        print("Trying with mono (1 channel)...")
        if channels != 1:
            # Retry with mono
            with wave.open(audio_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16", callback=callback):
                    print(f"Audio recording started (mono)... Audio will be saved as {audio_path}")
                    while not stop_event.is_set():
                        try:
                            data = q.get(timeout=0.1)
                        except queue.Empty:
                            continue
                        wf.writeframes(data.tobytes())
        else:
            raise

import cv2
import numpy as np
import pyautogui
import datetime
import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import sounddevice as sd
    import wave
except ImportError:
    sd = None
    wave = None

try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    try:
        # Fallback for older moviepy versions
        from moviepy.editor import VideoFileClip, AudioFileClip
    except ImportError:
        VideoFileClip = None
        AudioFileClip = None

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


def ensure_output_dir(path: str = "recordings") -> str:
    """Create output directory if it does not exist and return the path."""
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def record_audio(stop_event: threading.Event, audio_path: str, samplerate: int = 44100, channels: int = None):
    """
    Record microphone audio to a .wav file until stop_event is set.
    Requires the 'sounddevice' package: pip install sounddevice
    """
    if sd is None or wave is None:
        print("Audio recording is not available because 'sounddevice' is not installed.")
        print("Install it with: pip install sounddevice")
        return

    # Detect available channels from default input device
    if channels is None:
        try:
            device_info = sd.query_devices(kind='input')
            channels = device_info['max_input_channels']
            # Use mono (1) if device supports it, otherwise use what's available
            if channels > 1:
                channels = 1  # Most microphones are mono
            print(f"Using {channels} channel(s) for audio recording")
        except Exception as e:
            print(f"Warning: Could not detect audio device channels, using mono: {e}")
            channels = 1

    q: "queue.Queue[np.ndarray]" = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        q.put(indata.copy())

    try:
        with wave.open(audio_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(samplerate)

            with sd.InputStream(samplerate=samplerate, channels=channels, dtype="int16", callback=callback):
                print(f"Audio recording started... Audio will be saved as {audio_path}")
                while not stop_event.is_set():
                    try:
                        data = q.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    wf.writeframes(data.tobytes())
    except sd.PortAudioError as e:
        print(f"Error starting audio recording: {e}")
        print("Trying with mono (1 channel)...")
        if channels != 1:
            # Retry with mono
            with wave.open(audio_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16", callback=callback):
                    print(f"Audio recording started (mono)... Audio will be saved as {audio_path}")
                    while not stop_event.is_set():
                        try:
                            data = q.get(timeout=0.1)
                        except queue.Empty:
                            continue
                        wf.writeframes(data.tobytes())
        else:
            raise


def get_available_monitors():
    """Get list of available monitors."""
    monitors = []
    if MSS_AVAILABLE:
        with mss.mss() as sct:
            for i, monitor in enumerate(sct.monitors):
                if i == 0:
                    # Monitor 0 is "All monitors", skip it
                    continue
                monitors.append({
                    'index': i - 1,  # Adjust index (0-based for display)
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'left': monitor['left'],
                    'top': monitor['top']
                })
    else:
        # Fallback: single monitor
        screen_size = pyautogui.size()
        monitors.append({
            'index': 0,
            'width': screen_size.width,
            'height': screen_size.height,
            'left': 0,
            'top': 0
        })
    return monitors


def record_screen_region(stop_event, video_path, audio_path, final_mp4_path, monitor_info, status_callback=None):
    """
    Record a specific screen region to an .avi file and microphone to .wav.
    After recording, if moviepy is available, combine them into a single .mp4.
    """
    output_dir = ensure_output_dir()
    
    # Get screen dimensions
    if monitor_info:
        screen_size = (monitor_info['width'], monitor_info['height'])
        region = {
            'left': monitor_info['left'],
            'top': monitor_info['top'],
            'width': monitor_info['width'],
            'height': monitor_info['height']
        }
    else:
        screen_size = pyautogui.size()
        region = None

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_path, fourcc, 20.0, screen_size)

    if status_callback:
        status_callback("Recording started...")

    # Start audio recording thread (if sounddevice is available)
    audio_thread = None
    if sd is not None:
        audio_thread = threading.Thread(target=record_audio, args=(stop_event, audio_path), daemon=True)
        audio_thread.start()

    try:
        if MSS_AVAILABLE and region:
            # Use mss for multi-monitor support
            with mss.mss() as sct:
                while not stop_event.is_set():
                    # Capture specific monitor
                    screenshot = sct.grab(region)
                    frame = np.array(screenshot)
                    # mss returns BGRA, convert to BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    out.write(frame)
        else:
            # Fallback to pyautogui
            while not stop_event.is_set():
                img = pyautogui.screenshot()  # PIL Image in RGB
                frame = np.array(img)
                # Convert RGB (PIL) to BGR (OpenCV expects BGR)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame)
    finally:
        # Stop audio thread
        if audio_thread is not None:
            stop_event.set()
            audio_thread.join(timeout=2.0)

        out.release()
        cv2.destroyAllWindows()

        if status_callback:
            status_callback("Processing video...")

        # Combine video + audio into a single MP4 if moviepy is available
        if VideoFileClip is None:
            if status_callback:
                status_callback("Warning: moviepy not installed. Separate files saved.")
        elif not os.path.exists(video_path):
            if status_callback:
                status_callback("Error: Video file not found.")
        elif not os.path.exists(audio_path):
            if status_callback:
                status_callback("Warning: Audio file not found.")
        else:
            try:
                video_clip = VideoFileClip(video_path)
                audio_clip = AudioFileClip(audio_path)

                # Attach audio as-is using moviepy 2.x API (`with_audio`)
                video_with_audio = video_clip.with_audio(audio_clip)

                # Write final MP4
                video_with_audio.write_videofile(
                    final_mp4_path,
                    codec="libx264",
                    audio_codec="aac",
                    temp_audiofile=os.path.join(output_dir, f"temp_audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.m4a"),
                    remove_temp=True,
                )

                video_clip.close()
                audio_clip.close()
                video_with_audio.close()

                # Delete the intermediate files
                try:
                    os.remove(video_path)
                    os.remove(audio_path)
                except Exception:
                    pass

                if status_callback:
                    status_callback(f"✓ Success! MP4 saved: {os.path.basename(final_mp4_path)}")
                    
            except Exception as e:
                if status_callback:
                    status_callback(f"✗ Failed to create MP4: {str(e)}")


def record_screen_with_audio():
    """
    Record the entire screen to an .avi file (XVID codec) and microphone to .wav.
    After recording, if moviepy is available, combine them into a single .mp4 (video + audio).
    Stop with Ctrl+C in the terminal window. Video and audio filenames will match.
    """
    output_dir = ensure_output_dir()
    screen_size = pyautogui.size()

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    base_name = datetime.datetime.now().strftime("Video_%Y-%m-%d_%H-%M-%S")
    video_path = os.path.join(output_dir, f"{base_name}.avi")
    audio_path = os.path.join(output_dir, f"{base_name}.wav")
    final_mp4_path = os.path.join(output_dir, f"{base_name}.mp4")
    out = cv2.VideoWriter(video_path, fourcc, 20.0, screen_size)

    print("Recording started...")
    print(f"- Raw video will be saved as {video_path}")
    if sd is not None:
        print(f"- Raw audio will be saved as {audio_path}")
    if VideoFileClip is not None:
        print(f"After recording, a combined MP4 will be created as {final_mp4_path}")
    else:
        print("Note: To automatically create a single MP4 file, install moviepy:")
        print("      py -m pip install moviepy")
    print("Press Ctrl+C in this window to stop recording.")

    # Start audio recording thread (if sounddevice is available)
    stop_event = threading.Event()
    audio_thread = None
    if sd is not None:
        audio_thread = threading.Thread(target=record_audio, args=(stop_event, audio_path), daemon=True)
        audio_thread.start()

    try:
        while True:
            img = pyautogui.screenshot()  # PIL Image in RGB
            frame = np.array(img)
            # Convert RGB (PIL) to BGR (OpenCV expects BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    finally:
        # Stop audio thread
        if audio_thread is not None:
            stop_event.set()
            audio_thread.join(timeout=2.0)

        out.release()
        cv2.destroyAllWindows()

        # Combine video + audio into a single MP4 if moviepy is available
        if VideoFileClip is None:
            print("\nWarning: moviepy is not installed. Install it with: py -m pip install moviepy")
            print("You have separate .avi and .wav files.")
        elif not os.path.exists(video_path):
            print(f"\nWarning: Video file not found: {video_path}")
        elif not os.path.exists(audio_path):
            print(f"\nWarning: Audio file not found: {audio_path}")
            print("You have the video file but no audio was recorded.")
        else:
            try:
                print("\nCombining video and audio into a single MP4 file...")
                print("This may take a moment...")
                
                video_clip = VideoFileClip(video_path)
                audio_clip = AudioFileClip(audio_path)

                # Attach audio as-is using moviepy 2.x API (`with_audio`)
                # If audio is longer than video, extra audio won't be played.
                video_with_audio = video_clip.with_audio(audio_clip)

                # Write final MP4 (moviepy 2.x: no verbose/logger kwargs)
                video_with_audio.write_videofile(
                    final_mp4_path,
                    codec="libx264",
                    audio_codec="aac",
                    temp_audiofile=os.path.join(output_dir, f"{base_name}_temp_audio.m4a"),
                    remove_temp=True,
                )

                video_clip.close()
                audio_clip.close()
                video_with_audio.close()

                print(f"\n✓ Success! Combined MP4 saved as: {final_mp4_path}")
                
                # Delete the intermediate files
                try:
                    os.remove(video_path)
                    os.remove(audio_path)
                    print("✓ Removed intermediate .avi and .wav files")
                except Exception as e:
                    print(f"Note: Could not remove intermediate files: {e}")
                    
            except Exception as e:
                import traceback
                print(f"\n✗ Failed to create combined MP4: {e}")
                print("Error details:")
                traceback.print_exc()
                print("\nYou still have the separate .avi and .wav files.")


class ScreenRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Recorder")

        # Modern window sizing & centering
        window_width, window_height = 460, 460
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = int((screen_w - window_width) / 2)
        y = int((screen_h - window_height) / 3)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        # Set a light-modern background
        self.root.configure(bg="#f5f7fb")

        # Use ttk themed widgets
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Colors
        primary_color = "#2563eb"   # blue-600
        danger_color = "#dc2626"    # red-600
        text_main = "#111827"
        text_sub = "#6b7280"

        style.configure(
            "Card.TFrame",
            background="#ffffff",
            relief="flat",
        )
        style.configure(
            "Title.TLabel",
            background="#ffffff",
            foreground=text_main,
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#ffffff",
            foreground=text_sub,
            font=("Segoe UI", 9),
        )
        style.configure(
            "TLabel",
            background="#ffffff",
            foreground=text_main,
            font=("Segoe UI", 10),
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )
        style.map(
            "Primary.TButton",
            background=[("!disabled", primary_color), ("pressed", "#1d4ed8"), ("active", "#1d4ed8")],
            foreground=[("!disabled", "white")],
        )
        style.map(
            "Danger.TButton",
            background=[("!disabled", danger_color), ("pressed", "#b91c1c"), ("active", "#b91c1c")],
            foreground=[("!disabled", "white")],
        )

        self.is_recording = False
        self.stop_event = None
        self.recording_thread = None
        self.monitors = get_available_monitors()

        # Main card container
        outer = tk.Frame(self.root, bg="#f5f7fb")
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        card = ttk.Frame(outer, style="Card.TFrame", padding=16)
        card.pack(fill="both", expand=True)

        self.card = card
        self.primary_color = primary_color
        self.danger_color = danger_color
        self.text_sub = text_sub

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        card = self.card

        # Header
        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill="x")

        title_label = ttk.Label(header, text="Meeting Recorder", style="Title.TLabel")
        title_label.pack(anchor="w")

        subtitle = ttk.Label(
            header,
            text="Capture screen + microphone into a single MP4 file.",
            style="Subtitle.TLabel",
        )
        subtitle.pack(anchor="w", pady=(2, 8))

        # Screen selection row
        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x", pady=(4, 8))

        ttk.Label(row, text="Screen to record:").pack(side=tk.LEFT)

        self.screen_var = tk.StringVar()
        self.screen_combo = ttk.Combobox(
            row,
            textvariable=self.screen_var,
            state="readonly",
            width=28,
        )
        screen_options = [f"Screen {m['index'] + 1}  ({m['width']}×{m['height']})" for m in self.monitors]
        self.screen_combo["values"] = screen_options
        if screen_options:
            self.screen_combo.current(0)
        self.screen_combo.pack(side=tk.LEFT, padx=(8, 0))

        # Start/Stop button centered
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(12, 6))

        self.control_button = ttk.Button(
            btn_frame,
            text="Start recording",
            style="Primary.TButton",
            command=self.toggle_recording,
            width=22,
        )
        self.control_button.pack(pady=2)

        # Status label
        self.status_label = ttk.Label(card, text="Ready to record", style="Subtitle.TLabel")
        self.status_label.pack(anchor="w", pady=(6, 0))

        # Info label
        info_text = "Tip: For best results, close heavy apps you don't need while recording."
        ttk.Label(card, text=info_text, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        if not MSS_AVAILABLE:
            mss_text = "Multi-screen recording: install 'mss' →  py -m pip install mss"
            ttk.Label(card, text=mss_text, style="Subtitle.TLabel", foreground="#d97706").pack(
                anchor="w", pady=(2, 0)
            )
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        if not self.monitors:
            messagebox.showerror("Error", "No monitors detected!")
            return
        
        selected_index = self.screen_combo.current()
        if selected_index < 0:
            selected_index = 0
        
        monitor_info = self.monitors[selected_index]
        
        # Generate filenames
        output_dir = ensure_output_dir()
        base_name = datetime.datetime.now().strftime("Video_%Y-%m-%d_%H-%M-%S")
        video_path = os.path.join(output_dir, f"{base_name}.avi")
        audio_path = os.path.join(output_dir, f"{base_name}.wav")
        final_mp4_path = os.path.join(output_dir, f"{base_name}.mp4")
        
        # Update UI
        self.is_recording = True
        self.control_button.config(text="Stop recording", style="Danger.TButton")
        self.status_label.config(text=f"Recording screen {monitor_info['index'] + 1}…")
        self.screen_combo.config(state="disabled")
        
        # Start recording in separate thread
        self.stop_event = threading.Event()
        self.recording_thread = threading.Thread(
            target=record_screen_region,
            args=(self.stop_event, video_path, audio_path, final_mp4_path, monitor_info, self.update_status),
            daemon=True
        )
        self.recording_thread.start()
    
    def stop_recording(self):
        if self.stop_event:
            self.stop_event.set()
            self.status_label.config(text="Stopping recording…")
            self.control_button.config(state="disabled")
    
    def update_status(self, message):
        """Update status label from recording thread."""
        self.root.after(0, lambda: self.status_label.config(text=message, fg="blue" if "Success" in message else "red" if "Error" in message or "Failed" in message else "gray"))
        
        if "Success" in message or "Failed" in message or "Error" in message:
            # Recording finished, reset UI
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        """Reset UI to initial state."""
        self.is_recording = False
        self.control_button.config(text="Start recording", style="Primary.TButton", state="normal")
        self.screen_combo.config(state="readonly")
        if "Success" in self.status_label.cget("text"):
            self.status_label.config(text="Recording saved successfully!")
        else:
            self.status_label.config(text="Ready to record")


def launch_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = ScreenRecorderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    import sys
    # Check if GUI mode is requested (default) or CLI mode
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        record_screen_with_audio()
    else:
        launch_gui()

def record_screen_with_audio():
    """
    Record the entire screen to an .avi file (XVID codec) and microphone to .wav.
    After recording, if moviepy is available, combine them into a single .mp4 (video + audio).
    Stop with Ctrl+C in the terminal window. Video and audio filenames will match.
    """
    output_dir = ensure_output_dir()
    screen_size = pyautogui.size()

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    base_name = datetime.datetime.now().strftime("Video_%Y-%m-%d_%H-%M-%S")
    video_path = os.path.join(output_dir, f"{base_name}.avi")
    audio_path = os.path.join(output_dir, f"{base_name}.wav")
    final_mp4_path = os.path.join(output_dir, f"{base_name}.mp4")
    out = cv2.VideoWriter(video_path, fourcc, 20.0, screen_size)

    print("Recording started...")
    print(f"- Raw video will be saved as {video_path}")
    if sd is not None:
        print(f"- Raw audio will be saved as {audio_path}")
    if VideoFileClip is not None:
        print(f"After recording, a combined MP4 will be created as {final_mp4_path}")
    else:
        print("Note: To automatically create a single MP4 file, install moviepy:")
        print("      py -m pip install moviepy")
    print("Press Ctrl+C in this window to stop recording.")

    # Start audio recording thread (if sounddevice is available)
    stop_event = threading.Event()
    audio_thread = None
    if sd is not None:
        audio_thread = threading.Thread(target=record_audio, args=(stop_event, audio_path), daemon=True)
        audio_thread.start()

    try:
        while True:
            img = pyautogui.screenshot()  # PIL Image in RGB
            frame = np.array(img)
            # Convert RGB (PIL) to BGR (OpenCV expects BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    finally:
        # Stop audio thread
        if audio_thread is not None:
            stop_event.set()
            audio_thread.join(timeout=2.0)

        out.release()
        cv2.destroyAllWindows()

        # Combine video + audio into a single MP4 if moviepy is available
        if VideoFileClip is None:
            print("\nWarning: moviepy is not installed. Install it with: py -m pip install moviepy")
            print("You have separate .avi and .wav files.")
        elif not os.path.exists(video_path):
            print(f"\nWarning: Video file not found: {video_path}")
        elif not os.path.exists(audio_path):
            print(f"\nWarning: Audio file not found: {audio_path}")
            print("You have the video file but no audio was recorded.")
        else:
            try:
                print("\nCombining video and audio into a single MP4 file...")
                print("This may take a moment...")
                
                video_clip = VideoFileClip(video_path)
                audio_clip = AudioFileClip(audio_path)
                
                # Ensure audio duration matches video (trim if longer)
                if audio_clip.duration > video_clip.duration:
                    audio_clip = audio_clip.subclip(0, video_clip.duration)
                
                video_with_audio = video_clip.set_audio(audio_clip)

                # Write final MP4 with verbose output
                video_with_audio.write_videofile(
                    final_mp4_path,
                    codec="libx264",
                    audio_codec="aac",
                    temp_audiofile=os.path.join(output_dir, f"{base_name}_temp_audio.m4a"),
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )

                video_clip.close()
                audio_clip.close()
                video_with_audio.close()

                print(f"\n✓ Success! Combined MP4 saved as: {final_mp4_path}")
                
                # Delete the intermediate files
                try:
                    os.remove(video_path)
                    os.remove(audio_path)
                    print("✓ Removed intermediate .avi and .wav files")
                except Exception as e:
                    print(f"Note: Could not remove intermediate files: {e}")
                    
            except Exception as e:
                import traceback
                print(f"\n✗ Failed to create combined MP4: {e}")
                print("Error details:")
                traceback.print_exc()
                print("\nYou still have the separate .avi and .wav files.")


if __name__ == "__main__":
    record_screen_with_audio()
