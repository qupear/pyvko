# utils.py
import webbrowser
import os
from config import OUTPUT_HTML

def open_in_browser():
    """open in browser."""
    abs_path = os.path.abspath(OUTPUT_HTML)
    url = f"file://{abs_path}"
    try:
        webbrowser.open(url)
        print("🌐 Page opened in browser.")
    except Exception as e:
        print(f"❌ Cannot open page in browser: {e}")
