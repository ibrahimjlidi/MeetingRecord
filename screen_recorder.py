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
import time

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

try:
    import pygetwindow as gw
    WINDOW_DETECTION_AVAILABLE = True
except ImportError:
    WINDOW_DETECTION_AVAILABLE = False


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


def get_available_windows():
    """Get list of available application windows."""
    windows = []
    if WINDOW_DETECTION_AVAILABLE:
        try:
            all_windows = gw.getAllWindows()
            for win in all_windows:
                if win.title and win.visible and win.width > 0 and win.height > 0:
                    windows.append({
                        'title': win.title,
                        'left': win.left,
                        'top': win.top,
                        'width': win.width,
                        'height': win.height
                    })
        except Exception:
            pass
    return windows


def select_region_interactively():
    """Open a full-screen overlay to let user select a custom region."""
    class RegionSelector:
        def __init__(self):
            self.start_x = None
            self.start_y = None
            self.end_x = None
            self.end_y = None
            self.selected = False
            
            self.root = tk.Tk()
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-alpha', 0.3)
            self.root.configure(bg='black')
            self.root.attributes('-topmost', True)
            
            # Create canvas for drawing selection rectangle
            self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black', cursor='crosshair')
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Instructions
            self.canvas.create_text(
                self.root.winfo_screenwidth() // 2,
                50,
                text="Click and drag to select recording area | Press ESC to cancel",
                fill='white',
                font=('Arial', 16, 'bold')
            )
            
            self.canvas.bind('<Button-1>', self.on_click)
            self.canvas.bind('<B1-Motion>', self.on_drag)
            self.canvas.bind('<ButtonRelease-1>', self.on_release)
            self.root.bind('<Escape>', self.cancel)
            self.root.focus_set()
            
        def on_click(self, event):
            self.start_x = event.x
            self.start_y = event.y
            self.canvas.delete('rect')
            
        def on_drag(self, event):
            if self.start_x is not None:
                self.canvas.delete('rect')
                self.canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y,
                    outline='red', width=3, tags='rect'
                )
                
        def on_release(self, event):
            self.end_x = event.x
            self.end_y = event.y
            if self.start_x is not None:
                # Ensure coordinates are correct (start < end)
                left = min(self.start_x, self.end_x)
                top = min(self.start_y, self.end_y)
                right = max(self.start_x, self.end_x)
                bottom = max(self.start_y, self.end_y)
                
                if abs(right - left) > 50 and abs(bottom - top) > 50:  # Minimum size
                    self.selected = True
                    self.region = {
                        'left': left,
                        'top': top,
                        'width': right - left,
                        'height': bottom - top
                    }
                    self.root.quit()
                else:
                    self.canvas.delete('rect')
                    self.start_x = None
                    
        def cancel(self, event=None):
            self.selected = False
            self.root.quit()
            
        def get_region(self):
            self.root.mainloop()
            self.root.destroy()
            return self.region if self.selected else None
    
    selector = RegionSelector()
    return selector.get_region()


def record_screen_region(stop_event, video_path, audio_path, final_mp4_path, region_info=None, status_callback=None):
    """
    Record a specific screen region, window, or custom area to an .avi file and microphone to .wav.
    After recording, if moviepy is available, combine them into a single .mp4.
    
    region_info can be:
    - None: Full screen
    - dict with 'type': 'monitor', 'window', or 'custom' and corresponding coordinates
    """
    output_dir = ensure_output_dir()
    
    # Determine recording region
    if region_info and region_info.get('type') == 'window':
        # Window recording
        region = {
            'left': region_info['left'],
            'top': region_info['top'],
            'width': region_info['width'],
            'height': region_info['height']
        }
        screen_size = (region_info['width'], region_info['height'])
    elif region_info and region_info.get('type') == 'custom':
        # Custom region
        region = {
            'left': region_info['left'],
            'top': region_info['top'],
            'width': region_info['width'],
            'height': region_info['height']
        }
        screen_size = (region_info['width'], region_info['height'])
    elif region_info and region_info.get('type') == 'monitor':
        # Monitor recording
        screen_size = (region_info['width'], region_info['height'])
        region = {
            'left': region_info['left'],
            'top': region_info['top'],
            'width': region_info['width'],
            'height': region_info['height']
        }
    else:
        # Full screen fallback
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
            # Use mss for region/window/monitor recording
            with mss.mss() as sct:
                while not stop_event.is_set():
                    screenshot = sct.grab(region)
                    frame = np.array(screenshot)
                    # mss returns BGRA, convert to BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    out.write(frame)
        else:
            # Fallback to pyautogui (full screen only)
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
        window_width, window_height = 480, 580
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = int((screen_w - window_width) / 2)
        y = int((screen_h - window_height) / 3)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        # Dark theme background
        dark_bg = "#1e1e1e"
        dark_card = "#2d2d2d"
        dark_text = "#e0e0e0"
        dark_text_sub = "#a0a0a0"
        accent_red = "#dc2626"
        accent_blue = "#3b82f6"
        
        self.root.configure(bg=dark_bg)

        # Use ttk themed widgets
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Dark theme styles
        style.configure(
            "Card.TFrame",
            background=dark_card,
            relief="flat",
        )
        style.configure(
            "Title.TLabel",
            background=dark_card,
            foreground=dark_text,
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=dark_card,
            foreground=dark_text_sub,
            font=("Segoe UI", 9),
        )
        style.configure(
            "TLabel",
            background=dark_card,
            foreground=dark_text,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Timer.TLabel",
            background=dark_card,
            foreground="#ffffff",
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )
        style.map(
            "Primary.TButton",
            background=[("!disabled", accent_blue), ("pressed", "#2563eb"), ("active", "#2563eb")],
            foreground=[("!disabled", "white")],
        )
        style.map(
            "Danger.TButton",
            background=[("!disabled", accent_red), ("pressed", "#b91c1c"), ("active", "#b91c1c")],
            foreground=[("!disabled", "white")],
        )
        style.map(
            "Stop.TButton",
            background=[("!disabled", accent_red), ("pressed", "#b91c1c"), ("active", "#b91c1c")],
            foreground=[("!disabled", "white")],
        )
        
        # Radio button dark theme
        style.configure(
            "TRadiobutton",
            background=dark_card,
            foreground=dark_text,
            font=("Segoe UI", 9),
        )
        style.map(
            "TRadiobutton",
            background=[("selected", dark_card)],
            foreground=[("selected", dark_text)],
        )
        
        # Combobox dark theme
        style.configure(
            "TCombobox",
            fieldbackground=dark_card,
            background=dark_card,
            foreground=dark_text,
            borderwidth=1,
        )

        # Store theme colors on the instance before creating child widgets
        self.dark_bg = dark_bg
        self.dark_card = dark_card
        self.dark_text = dark_text
        self.dark_text_sub = dark_text_sub
        self.accent_red = accent_red
        self.accent_blue = accent_blue

        self.is_recording = False
        self.stop_event = None
        self.recording_thread = None
        self.record_start_time = None
        self.timer_job = None
        self.monitors = get_available_monitors()
        self.windows = get_available_windows() if WINDOW_DETECTION_AVAILABLE else []
        self.selected_region = None

        # Main card container
        outer = tk.Frame(self.root, bg=self.dark_bg)
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        card = ttk.Frame(outer, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)

        self.card = card

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        card = self.card

        # Header
        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill="x", pady=(0, 8))

        title_label = ttk.Label(header, text="Meeting Recorder", style="Title.TLabel")
        title_label.pack(anchor="w")

        subtitle = ttk.Label(
            header,
            text="Capture screen + microphone into a single MP4 file.",
            style="Subtitle.TLabel",
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Recording mode selection
        mode_frame = ttk.Frame(card, style="Card.TFrame")
        mode_frame.pack(fill="x", pady=(4, 8))
        
        ttk.Label(mode_frame, text="Recording mode:").pack(anchor="w")
        
        self.mode_var = tk.StringVar(value="monitor")
        mode_options_frame = ttk.Frame(mode_frame, style="Card.TFrame")
        mode_options_frame.pack(fill="x", pady=(4, 0))
        
        ttk.Radiobutton(
            mode_options_frame,
            text="Full Screen",
            variable=self.mode_var,
            value="monitor",
            command=self.on_mode_change
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        ttk.Radiobutton(
            mode_options_frame,
            text="Window",
            variable=self.mode_var,
            value="window",
            command=self.on_mode_change
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        ttk.Radiobutton(
            mode_options_frame,
            text="Custom Region",
            variable=self.mode_var,
            value="custom",
            command=self.on_mode_change
        ).pack(side=tk.LEFT)
        
        # Dynamic selection frame
        self.selection_frame = ttk.Frame(card, style="Card.TFrame")
        self.selection_frame.pack(fill="x", pady=(8, 0))
        
        # Monitor selection
        self.monitor_row = ttk.Frame(self.selection_frame, style="Card.TFrame")
        ttk.Label(self.monitor_row, text="Select monitor:").pack(side=tk.LEFT)
        self.screen_var = tk.StringVar()
        self.screen_combo = ttk.Combobox(
            self.monitor_row,
            textvariable=self.screen_var,
            state="readonly",
            width=25,
        )
        screen_options = [f"Screen {m['index'] + 1}  ({m['width']}×{m['height']})" for m in self.monitors]
        self.screen_combo["values"] = screen_options
        if screen_options:
            self.screen_combo.current(0)
        self.screen_combo.pack(side=tk.LEFT, padx=(8, 0))
        
        # Window selection
        self.window_row = ttk.Frame(self.selection_frame, style="Card.TFrame")
        ttk.Label(self.window_row, text="Select window:").pack(side=tk.LEFT)
        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(
            self.window_row,
            textvariable=self.window_var,
            state="readonly",
            width=25,
        )
        window_options = [f"{w['title'][:40]} ({w['width']}×{w['height']})" for w in self.windows[:50]]  # Limit to 50 windows
        self.window_combo["values"] = window_options
        if window_options:
            self.window_combo.current(0)
        self.window_combo.pack(side=tk.LEFT, padx=(8, 0))
        
        # Custom region button
        self.custom_row = ttk.Frame(self.selection_frame, style="Card.TFrame")
        self.select_region_btn = ttk.Button(
            self.custom_row,
            text="Select Region",
            command=self.select_custom_region,
            width=20
        )
        self.select_region_btn.pack(side=tk.LEFT)
        self.region_label = ttk.Label(self.custom_row, text="", style="Subtitle.TLabel")
        self.region_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Show initial mode
        self.on_mode_change()

        # Timer Status Panel (prominent display like Capture Status)
        timer_frame = tk.Frame(card, bg=self.dark_card, relief="flat")
        timer_frame.pack(fill="x", pady=(16, 12), padx=0)
        
        # Left side: Recording indicator + Timer
        timer_left = tk.Frame(timer_frame, bg=self.dark_card)
        timer_left.pack(side=tk.LEFT, fill="x", expand=True, padx=12, pady=12)
        
        # Recording indicator circle (hidden initially)
        self.recording_indicator = tk.Canvas(timer_left, width=16, height=16, bg=self.dark_card, highlightthickness=0)
        self.recording_indicator.pack(side=tk.LEFT, padx=(0, 12))
        self.indicator_circle = self.recording_indicator.create_oval(4, 4, 12, 12, fill="#666666", outline="")
        
        # Timer display (large and prominent)
        self.timer_label = tk.Label(
            timer_left,
            text="0:00:00",
            bg=self.dark_card,
            fg="#ffffff",
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        )
        self.timer_label.pack(side=tk.LEFT, fill="x", expand=True)
        
        # Right side: Stop button (hidden initially)
        timer_right = tk.Frame(timer_frame, bg=self.dark_card)
        timer_right.pack(side=tk.RIGHT, padx=(0, 12), pady=8)
        
        self.stop_button = tk.Button(
            timer_right,
            text="⏹",
            command=self.toggle_recording,
            bg=self.accent_red,
            fg="white",
            font=("Segoe UI", 14),
            relief="flat",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            state="disabled"
        )
        self.stop_button.pack()

        # Start/Stop button
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(8, 6))

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
        
    def on_mode_change(self):
        """Update UI based on selected recording mode."""
        mode = self.mode_var.get()
        
        # Hide all selection rows
        self.monitor_row.pack_forget()
        self.window_row.pack_forget()
        self.custom_row.pack_forget()
        
        # Show appropriate selection
        if mode == "monitor":
            self.monitor_row.pack(fill="x", pady=(4, 0))
        elif mode == "window":
            if not WINDOW_DETECTION_AVAILABLE:
                messagebox.showwarning("Window Detection", "Install 'pygetwindow' for window selection:\npy -m pip install pygetwindow")
                self.mode_var.set("monitor")
                self.on_mode_change()
                return
            if not self.windows:
                messagebox.showwarning("No Windows", "No windows detected. Please open some applications.")
                self.mode_var.set("monitor")
                self.on_mode_change()
                return
            self.window_row.pack(fill="x", pady=(4, 0))
        elif mode == "custom":
            self.custom_row.pack(fill="x", pady=(4, 0))
    
    def select_custom_region(self):
        """Open region selector overlay."""
        self.root.withdraw()  # Hide main window
        region = select_region_interactively()
        self.root.deiconify()  # Show main window again
        
        if region:
            self.selected_region = region
            self.region_label.config(
                text=f"Region: {region['width']}×{region['height']} at ({region['left']}, {region['top']})"
            )
        else:
            self.selected_region = None
            self.region_label.config(text="")
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        mode = self.mode_var.get()
        region_info = None
        
        if mode == "monitor":
            if not self.monitors:
                messagebox.showerror("Error", "No monitors detected!")
                return
            selected_index = self.screen_combo.current()
            if selected_index < 0:
                selected_index = 0
            monitor = self.monitors[selected_index]
            region_info = {
                'type': 'monitor',
                'left': monitor['left'],
                'top': monitor['top'],
                'width': monitor['width'],
                'height': monitor['height']
            }
            status_text = f"Recording screen {monitor['index'] + 1}…"
            
        elif mode == "window":
            if not self.windows:
                messagebox.showerror("Error", "No windows available!")
                return
            selected_index = self.window_combo.current()
            if selected_index < 0:
                selected_index = 0
            window = self.windows[selected_index]
            region_info = {
                'type': 'window',
                'left': window['left'],
                'top': window['top'],
                'width': window['width'],
                'height': window['height']
            }
            status_text = f"Recording window: {window['title'][:30]}…"
            
        elif mode == "custom":
            if not self.selected_region:
                messagebox.showwarning("No Region", "Please select a custom region first.")
                return
            region_info = {
                'type': 'custom',
                'left': self.selected_region['left'],
                'top': self.selected_region['top'],
                'width': self.selected_region['width'],
                'height': self.selected_region['height']
            }
            status_text = f"Recording custom region ({region_info['width']}×{region_info['height']})…"
        
        # Generate filenames
        output_dir = ensure_output_dir()
        base_name = datetime.datetime.now().strftime("Video_%Y-%m-%d_%H-%M-%S")
        video_path = os.path.join(output_dir, f"{base_name}.avi")
        audio_path = os.path.join(output_dir, f"{base_name}.wav")
        final_mp4_path = os.path.join(output_dir, f"{base_name}.mp4")
        
        # Update UI
        self.is_recording = True
        self.record_start_time = time.time()
        self.start_timer()
        # Show recording indicator and stop button
        self.recording_indicator.itemconfig(self.indicator_circle, fill=self.accent_red)
        self.stop_button.config(state="normal")
        self.control_button.config(text="Stop recording", style="Danger.TButton")
        self.status_label.config(text=status_text)
        self.screen_combo.config(state="disabled")
        self.window_combo.config(state="disabled")
        self.select_region_btn.config(state="disabled")
        
        # Start recording in separate thread
        self.stop_event = threading.Event()
        self.recording_thread = threading.Thread(
            target=record_screen_region,
            args=(self.stop_event, video_path, audio_path, final_mp4_path, region_info, self.update_status),
            daemon=True
        )
        self.recording_thread.start()
    
    def stop_recording(self):
        if self.stop_event:
            self.stop_event.set()
            self.status_label.config(text="Stopping recording…")
            self.control_button.config(state="disabled")
            # Stop timer; final update will happen in reset_ui
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None
    
    def update_status(self, message):
        """Update status label from recording thread."""
        self.root.after(0, lambda: self.status_label.config(text=message, fg="blue" if "Success" in message else "red" if "Error" in message or "Failed" in message else "gray"))
        
        if "Success" in message or "Failed" in message or "Error" in message:
            # Recording finished, reset UI
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        """Reset UI to initial state."""
        self.is_recording = False
        # Hide recording indicator and stop button
        self.recording_indicator.itemconfig(self.indicator_circle, fill="#666666")
        self.stop_button.config(state="disabled")
        self.control_button.config(text="Start recording", style="Primary.TButton", state="normal")
        self.screen_combo.config(state="readonly")
        self.window_combo.config(state="readonly")
        self.select_region_btn.config(state="normal")
        self.record_start_time = None
        self.timer_label.config(text="0:00:00")
        if "Success" in self.status_label.cget("text"):
            self.status_label.config(text="Recording saved successfully!")
        else:
            self.status_label.config(text="Ready to record")

    def start_timer(self):
        """Start or continue updating the elapsed time label."""
        if not self.is_recording or self.record_start_time is None:
            return

        elapsed = int(time.time() - self.record_start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        # Format: 0:00:00 (single digit hours, like in the image)
        self.timer_label.config(text=f"{hours}:{minutes:02d}:{seconds:02d}")

        # Schedule next update
        self.timer_job = self.root.after(1000, self.start_timer)


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
