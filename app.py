import gradio as gr
import requests
import base64
import json
import time
import os
from typing import Dict, Optional
from PIL import Image
import io
import numpy as np
import logging

# Configuration
CONFIG_PATH = os.path.join(os.getcwd(), 'api_config.json')
DRIVERS = [
    "bank://lively/driver-01",
    "bank://lively/driver-02",
    "bank://lively/driver-05",
    "bank://serious/driver-03",
    "bank://happy/driver-04"
]

def load_config() -> Dict:
    """Load configuration with Windows path support"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Config error: {str(e)}")
        return {"key": "", "url": "https://api.d-id.com"}

config = load_config()
API_KEY = config.get("key")
BASE_URL = config.get("url", "https://api.d-id.com")

def validate_image_url(url: str):
    """Check if image URL is valid and return numpy array"""
    try:
        if not url or not url.strip() or not url.startswith(('http://', 'https://')):
            return None, "❌ Please enter a valid URL starting with http:// or https://"
            
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        img.verify()
        img = Image.open(io.BytesIO(response.content))
        img.thumbnail((200, 200))
        return np.array(img), "✅ Valid avatar image"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def validate_audio_url(url: str):
    """Check if audio URL is valid MP3 and return URL"""
    try:
        if not url or not url.strip() or not url.startswith(('http://', 'https://')):
            return None, "❌ Please enter a valid URL starting with http:// or https://"
            
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        if 'mp3' not in content_type and 'mpeg' not in content_type:
            return None, "❌ Only MP3 audio files are supported"
            
        return url, "✅ Valid MP3 audio file"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

class DIDClient:
    def __init__(self, api_key: str):
        self.headers = {
            "Authorization": f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
    
    def create_talk(self, payload: Dict) -> Dict:
        response = requests.post(
            f"{BASE_URL}/talks",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_talk(self, talk_id: str) -> Dict:
        response = requests.get(
            f"{BASE_URL}/talks/{talk_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

def download_video(url: str) -> str:
    """Windows-safe video downloader with progress tracking"""
    if not url.startswith(('http://', 'https://')):
        return None, "❌ Invalid URL"
    
    os.makedirs('d-id_videos', exist_ok=True)
    filename = os.path.join('d-id_videos', f"video_{int(time.time())}.mp4")
    
    try:
        with requests.get(url, stream=True, timeout=(10, 30)) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
                        downloaded += len(chunk)
            
        return filename, "✅ Downloaded successfully"
    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        return None, f"❌ Download failed: {str(e)}"

def create_app_interface():
    with gr.Blocks(title="D-ID Studio Pro", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎬 D-ID Studio Pro - Complete Workflow")
        
        # ======== Create Video Tab ========
        with gr.Tab("Create Video"):
            with gr.Row():
                with gr.Column():
                    # Source Configuration
                    with gr.Group():
                        source_url = gr.Textbox(
                            label="Source Image URL",
                            value="https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg",
                            placeholder="Enter direct image URL"
                        )
                        preview_status = gr.Textbox(
                            label="Image Status", 
                            value="✅ Default avatar loaded",
                            interactive=False
                        )
                        image_preview = gr.Image(
                            label="Avatar Preview", 
                            height=200
                        )
                    
                    # Script Configuration
                    script_type = gr.Radio(
                        label="Script Type",
                        choices=["text", "audio"],
                        value="text"
                    )
                    
                    with gr.Group(visible=True) as text_script_group:
                        text_input = gr.TextArea(
                            label="Text Script",
                            value="Hello world!"
                        )
                        with gr.Row():
                            voice_provider = gr.Dropdown(
                                label="TTS Provider",
                                choices=["microsoft", "amazon", "google"],
                                value="microsoft"
                            )
                            voice_id = gr.Textbox(
                                label="Voice ID",
                                value="en-US-JennyNeural"
                            )
                    
                    with gr.Group(visible=False) as audio_script_group:
                        audio_url = gr.Textbox(
                            label="Audio File URL (MP3 only)",
                            value="https://d-id-public-bucket.s3.us-west-2.amazonaws.com/webrtc.mp3",
                            placeholder="https://example.com/audio.mp3"
                        )
                        audio_status = gr.Textbox(
                            label="Audio Status",
                            value="✅ Default audio loaded",
                            interactive=False
                        )
                        audio_preview = gr.Audio(
                            label="Audio Preview",
                            visible=True
                        )
                    
                    # Advanced Configuration
                    with gr.Accordion("Advanced Options", open=False):
                        with gr.Row():
                            stitch = gr.Checkbox(label="Enable Stitch")
                            persist = gr.Checkbox(label="Persist Video")
                        driver_url = gr.Dropdown(
                            label="Driver Selection (Optional)",
                            choices=[""] + DRIVERS,
                            value=""
                        )
                        voice_style = gr.Textbox(
                            label="Voice Style (Optional)",
                            placeholder="e.g., Cheerful, Friendly"
                        )
                        webhook = gr.Textbox(
                            label="Webhook URL",
                            placeholder="https://your-server.com/webhook"
                        )
                        external_tts = gr.Textbox(
                            label="External TTS Key",
                            placeholder='{"elevenlabs": "YOUR_KEY"}'
                        )
                    
                    submit_btn = gr.Button("Create Talk", variant="primary")
                
                with gr.Column():
                    talk_id = gr.Textbox(label="Talk ID", interactive=False)
                    status = gr.Textbox(label="Status", interactive=False)
                    
                    # Combined Result URL and Download
                    with gr.Group():
                        with gr.Row():
                            result_url = gr.Textbox(
                                label="Result URL", 
                                interactive=False,
                                scale=4
                            )
                            download_btn = gr.Button(
                                "⬇️ Download Video",
                                variant="primary",
                                scale=1
                            )
                    
                    # Smaller video preview
                    video_preview = gr.Video(
                        label="Generated Video Preview", 
                        visible=False, 
                        height=240
                    )
                    
                    # Download status and preview
                    download_status = gr.Textbox(
                        label="Download Status",
                        visible=False
                    )
                    local_video_preview = gr.Video(
                        label="Downloaded Video", 
                        visible=False,
                        height=240
                    )
                    
                    # Debug Logs - Collapsed by default
                    with gr.Accordion("Debug Logs", open=False):
                        api_logs = gr.Textbox(
                            label="", 
                            interactive=False,
                            lines=8,
                            max_lines=20,
                            show_label=False
                        )
        
        # ======== Config Tab ========
        with gr.Tab("Config"):
            gr.Markdown("### API Configuration")
            with gr.Row():
                with gr.Column():
                    gr.Markdown(f"**Config File Location:**  \n`{CONFIG_PATH}`")
                    api_status = gr.Markdown(f"**API Status:**  \n{'🟢 Connected' if API_KEY else '🔴 Not Configured'}")
                    
                    with gr.Accordion("Edit Config", open=False):
                        new_api_key = gr.Textbox(
                            label="API Key",
                            value=API_KEY,
                            type="password"
                        )
                        new_api_url = gr.Textbox(
                            label="API URL",
                            value=BASE_URL
                        )
                        with gr.Row():
                            save_btn = gr.Button("Save Config")
                            test_btn = gr.Button("Test API Key", variant="secondary")
                        save_status = gr.Textbox(label="", visible=False)
                        test_output = gr.JSON(label="API Credits", visible=False)
                
                with gr.Column():
                    gr.Markdown("### Configuration Help")
                    gr.Code("""{
  "key": "your_api_key_here",
  "url": "https://api.d-id.com"
}""", language="json")
                    gr.Markdown("""
- Save this as `api_config.json` in the same folder
- Restart the app after changes
- Use environment variables for production
""")
        
        # ======== Event Handlers ========
        # Load default media on app start
        def load_default_media():
            img_array, _ = validate_image_url("https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg")
            audio_url, _ = validate_audio_url("https://d-id-public-bucket.s3.us-west-2.amazonaws.com/webrtc.mp3")
            return img_array, audio_url
        
        app.load(load_default_media, outputs=[image_preview, audio_preview])
        
        # Automatic image preview when URL changes
        def update_image_preview(url):
            if not url:
                return None, "❌ Please enter an image URL", gr.Image(visible=False)
            
            img_array, message = validate_image_url(url)
            if img_array is not None:
                return img_array, message, gr.Image(visible=True)
            return None, message, gr.Image(visible=False)

        source_url.change(
            fn=update_image_preview,
            inputs=source_url,
            outputs=[image_preview, preview_status, image_preview]
        )
        
        # Automatic audio preview when URL changes
        def update_audio_preview(url):
            if not url:
                return None, "❌ Please enter an audio URL", gr.Audio(visible=False)
            
            audio_url, message = validate_audio_url(url)
            if audio_url is not None:
                return audio_url, message, gr.Audio(visible=True)
            return None, message, gr.Audio(visible=False)

        audio_url.change(
            fn=update_audio_preview,
            inputs=audio_url,
            outputs=[audio_preview, audio_status, audio_preview]
        )
        
        # Dynamic UI Updates
        script_type.change(
            fn=lambda x: (gr.Group(visible=x == "text"), gr.Group(visible=x == "audio")),
            inputs=script_type,
            outputs=[text_script_group, audio_script_group]
        )
        
        # Create Talk Submission
        def create_talk(*args):
            try:
                if not API_KEY:
                    yield "", "Error: No API key", "", gr.Video(visible=False), "", "Configure API key first"
                    return
                    
                client = DIDClient(API_KEY)
                
                # Build payload according to API reference
                payload = {
                    "source_url": args[0],
                    "script": {
                        "type": args[1],
                        "input": args[2] if args[1] == "text" else "",
                        "subtitles": "false",
                        "ssml": "false",
                        "provider": {
                            "type": args[4],
                            "voice_id": args[5],
                            **({"voice_config": {"style": args[6]}} if args[6] else {})
                        } if args[1] == "text" else None,
                        "audio_url": args[3] if args[1] == "audio" else None
                    },
                    "config": {
                        "fluent": "false",
                        **({"stitch": True} if args[9] else {}),
                        **({"persist": True} if args[10] else {}),
                        **({"webhook": args[8]} if args[8] else {})
                    },
                    **({"driver_url": args[7]} if args[7] else {})
                }

                # Remove None values
                payload = {k: v for k, v in payload.items() if v is not None}
                payload["script"] = {k: v for k, v in payload["script"].items() if v is not None}
                
                # Initial API call to create talk
                talk = client.create_talk(payload)
                response_log = f"Creation Response:\n{json.dumps(talk, indent=2)}"
                
                if not talk.get("id"):
                    yield "", "Failed", "", gr.Video(visible=False), "", response_log
                    return
                
                # Poll for completion with progress updates
                talk_id = talk["id"]
                start_time = time.time()
                timeout = 300  # 5 minutes timeout
                poll_interval = 2  # seconds
                
                while time.time() - start_time < timeout:
                    # Get talk status
                    talk_status = client.get_talk(talk_id)
                    current_status = talk_status.get("status", "unknown")
                    response_log += f"\n\nPolling Response ({current_status}):\n{json.dumps(talk_status, indent=2)}"
                    
                    # Update status in UI
                    yield (
                        talk_id,
                        f"Status: {current_status}",
                        talk_status.get("result_url", ""),
                        gr.Video(visible=False),
                        "",
                        response_log
                    )
                    
                    # Check if processing is complete
                    if current_status == "done":
                        result_url = talk_status.get("result_url")
                        if result_url:
                            yield (
                                talk_id,
                                "Completed successfully",
                                result_url,
                                gr.Video(value=result_url, visible=True),
                                "",
                                response_log
                            )
                            return
                        break
                    elif current_status in ["failed", "error"]:
                        break
                        
                    time.sleep(poll_interval)
                
                # If we get here, processing didn't complete successfully
                yield (
                    talk_id,
                    f"Processing timed out or failed (status: {current_status})",
                    "",
                    gr.Video(visible=False),
                    "",
                    response_log
                )
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                if hasattr(e, 'response') and e.response:
                    error_msg += f"\nAPI Response:\n{e.response.text}"
                yield "", "Error", "", gr.Video(visible=False), "", error_msg

        submit_btn.click(
            fn=create_talk,
            inputs=[
                source_url, script_type, text_input, audio_url,
                voice_provider, voice_id, voice_style, driver_url,
                webhook, stitch, persist, external_tts
            ],
            outputs=[talk_id, status, result_url, video_preview, download_status, api_logs],
            api_name="create_talk"
        )
        
        # Download Handler
        def download_handler(url):
            try:
                if not url:
                    return "⬇️ Download Video", "❌ No URL provided", gr.Video(visible=False)
                
                # Show downloading state
                yield "⏳ Downloading...", "Download started...", gr.Video(visible=False)
                
                filepath, message = download_video(url)
                if filepath:
                    yield "✅ Download Complete", message, gr.Video(value=filepath, visible=True)
                else:
                    yield "❌ Download Failed", message, gr.Video(visible=False)
                    
            except Exception as e:
                yield "❌ Download Failed", f"❌ Error: {str(e)}", gr.Video(visible=False)

        download_btn.click(
            fn=download_handler,
            inputs=result_url,
            outputs=[download_btn, download_status, local_video_preview]
        )
        
        # Config Save Handler
        def save_config_handler(key, url):
            try:
                config = {"key": key, "url": url}
                with open(CONFIG_PATH, 'w') as f:
                    json.dump(config, f)
                global API_KEY, BASE_URL
                API_KEY = key
                BASE_URL = url
                return "✅ Config saved! Restart app to apply changes", gr.Markdown(f"**API Status:**  \n{'🟢 Connected' if key else '🔴 Not Configured'}")
            except Exception as e:
                return f"❌ Error saving config: {str(e)}", gr.Markdown(f"**API Status:**  \n{'🟢 Connected' if API_KEY else '🔴 Not Configured'}")

        save_btn.click(
            fn=save_config_handler,
            inputs=[new_api_key, new_api_url],
            outputs=[save_status, api_status]
        )
        
        # API Test Handler
        def test_api_key(api_key):
            if not api_key:
                return gr.JSON(visible=False), "❌ Please enter an API key first"
            
            try:
                headers = {
                    "Authorization": f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}",
                    "accept": "application/json"
                }
                response = requests.get(f"{BASE_URL}/credits", headers=headers)
                response.raise_for_status()
                data = response.json()
                
                credits_summary = {
                    "remaining": data.get("remaining"),
                    "total": data.get("total"),
                    "expiry": data.get("expiry")
                }
                return credits_summary, "✅ API Key is valid", gr.JSON(visible=True)
            except Exception as e:
                return {}, f"❌ API Key test failed: {str(e)}", gr.JSON(visible=False)

        test_btn.click(
            fn=test_api_key,
            inputs=new_api_key,
            outputs=[test_output, save_status, test_output]
        )

        return app

if __name__ == "__main__":
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"key": "", "url": "https://api.d-id.com"}, f)
        print(f"⚠️ Created default config file at: {CONFIG_PATH}")
    
    if not API_KEY or not API_KEY.strip():
        print("⚠️ Warning: No API key configured in api_config.json")

    # Suppress noisy asyncio connection errors on Windows
    if os.name == "nt":
        logging.getLogger("asyncio").setLevel(logging.ERROR)

    app = create_app_interface()
    app.launch()
