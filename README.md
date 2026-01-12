## Meeting Recorder

A simple **screen + audio recorder** for Windows that:
- Captures a selected monitor
- Records your microphone
- Automatically combines them into a **single MP4 file**
- Provides a small **GUI** (Start / Stop + screen selector)

---

### 1. Requirements

- **OS**: Windows 10 (or later)
- **Python**: 3.13 (already installed on your machine)
- Tools:
  - `py` launcher (you already use `py screen_recorder.py`)

---

### 2. Setup (first time)

Open PowerShell in the project folder:

```powershell
cd C:\Users\brahim\MeetingRecorder
```

#### 2.1. Create a virtual environment (optional but recommended)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

> If activation is blocked, allow scripts once:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

#### 2.2. Install dependencies

Install all required Python packages:

```powershell
py -m pip install -r requirements.txt
```

If that fails, you can install them one by one:

```powershell
py -m pip install opencv-python numpy pyautogui sounddevice moviepy mss
```

---

### 3. How to use

From the project folder:

```powershell
cd C:\Users\brahim\MeetingRecorder
py screen_recorder.py
```

The **GUI** will open:

1. **Select Screen**  
   - Use the dropdown to choose which monitor you want to record.
2. **Start recording**  
   - Click **“Start recording”**.
   - The app starts recording the chosen screen and your microphone.
3. **Stop recording**  
   - Click **“Stop recording”** to finish.
4. **Output files**  
   - A final MP4 file is saved in the `recordings` folder, for example:
     - `recordings/Video_YYYY-MM-DD_HH-MM-SS.mp4`
   - Intermediate `.avi` and `.wav` files are removed automatically once the MP4 is created.

#### 3.1. Command line (no GUI)

If you prefer the old terminal mode:

```powershell
py screen_recorder.py --cli
```

Stop recording with **Ctrl + C** in the terminal.

---

### 4. Project structure

```text
MeetingRecorder/
  screen_recorder.py   # Main application (GUI + recording logic)
  audio_recorder.py    # (currently unused / placeholder)
  recordings/          # Output videos (MP4) and intermediates
  requirements.txt     # Python dependencies
  README.md            # This file
```

---

### 5. Add and push to GitHub

#### 5.1. Initialize Git (only once)

In PowerShell, inside the project folder:

```powershell
cd C:\Users\brahim\MeetingRecorder
git init
git add .
git commit -m "Initial commit: meeting recorder with GUI"
```

#### 5.2. Create a GitHub repository

1. Go to `https://github.com` in your browser.
2. Click **“New”** repository.
3. Choose a name, for example: `MeetingRecorder`.
4. **Do NOT** add a README from GitHub (you already have one).
5. Create the repository.

GitHub will show you the **remote URL**, something like:

```text
https://github.com/<your-username>/MeetingRecorder.git
```

#### 5.3. Connect local project to GitHub and push

Replace `<your-username>` with your real GitHub username:

```powershell
cd C:\Users\brahim\MeetingRecorder
git remote add origin https://github.com/<your-username>/MeetingRecorder.git
git branch -M main
git push -u origin main
```

After this, your project will be on GitHub.  
Next time you make changes:

```powershell
git add .
git commit -m "Describe your change"
git push
```

---

### 6. Notes / Tips

- If audio doesn’t record, check your microphone is enabled in Windows and not used by another app.
- If multi-monitor selection doesn’t work, ensure `mss` installed correctly:
  ```powershell
  py -m pip install mss
  ```
- If any dependency fails, reinstall using:
  ```powershell
  py -m pip install --upgrade pip
  py -m pip install -r requirements.txt
  ```

