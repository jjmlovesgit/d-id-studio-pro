![image](https://github.com/user-attachments/assets/873c64bd-131f-4a1e-a72a-8e70e0f831eb)
# 🎨 D-ID Studio Pro

D-ID Studio Pro is a Gradio-powered local app for generating AI-driven talking head videos using the D-ID API. It features a clean, no-code interface with support for text or audio scripts, voice selection, driver customization, and media previews.

## 🚀 Quick Start

### ✅ 1. Clone the Repo

```
git clone https://github.com/jjmlovesgit/d-id-studio-pro.git
cd d-id-studio-pro
```

### ✅ 2. Run the Setup Script

```bash
python setup.py
```

This will:

- Create a local Python virtual environment
- Install all required dependencies (always installs the latest Gradio)
- Optionally launch the app immediately 
- Note:  You must add/save your D-id API Key after launching the app using the config tab "Edit config" selection  

## 🧐 Features

- 🖼 Avatar preview from image URL
- 🎤 Supports text and audio scripts
- 🌊 Voice provider selection (Microsoft, Amazon, Google)
- 📃 Voice styles + driver options
- 🔁 Polling + live status updates
- 📅 Download generated video locally
- 🤩 Config tab with live key editing & test

## 🦪 How to Run Later

### 🪟 Windows

#### 🔠 Use the One-Click Launcher (Recommended)

You can launch the app easily using the included batch file:

1. Locate `launch_app.bat` in the root of the project  
2. Right-click → **Send to → Desktop (Create Shortcut)**  
3. Rename the shortcut to: `Run D-ID Studio Pro`  
4. Double-click to launch the app from your desktop!

> This will activate the virtual environment and run the app in one click.

Or run manually:

```bash
.
env\Scripts ctivate
python app.py
```

### 🍎 macOS / Linux

```bash
source venv/bin/activate
python app.py
```

## 🔐 API Configuration

The setup script creates a file called `api_config.json`, or you can copy the included template file:

```json
{
  "key": "Add your D-id key",
  "url": "https://api.d-id.com"
}
```

> `api_config.json` is excluded from version control by default (see `.gitignore`).

You can edit it manually or through the app's Config tab.

## 📦 Requirements

- Python 3.8+
- Internet access for API requests
- Free or paid D-ID API Key

## 🗃 File Structure

```text
d-id-studio-pro/
├── app.py               # Main Gradio app
├── setup.py             # Setup + install script
├── launch_app.bat       # (Optional) Windows one-click launcher
├── launch_app.sh        # (Optional) macOS/Linux launcher
├── api_config.json      # Config file (auto-generated)
├── requirements.txt     # Dependency list
├── .gitignore           # Excludes sensitive files
└── README.md
```

## 📄 License

MIT License. Not affiliated with D-ID. Use responsibly.
