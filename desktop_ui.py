import webview
import threading
import os
from polling_ui.app import app  # Make sure your Flask app is importable

# Optional: Set the working directory to polling_ui
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(BASE_DIR, "polling_ui"))

def start_flask():
    """
    Starts the Flask server on localhost in a separate thread.
    """
    app.run(debug=False, port=5000, use_reloader=False)  # use_reloader=False prevents double-start

if __name__ == "__main__":
    # Start Flask in a background thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Open a desktop window pointing to the Flask app
    webview.create_window(
        "Polling UI",                   # Window title
        "http://127.0.0.1:5000",        # URL of your Flask app
        fullscreen=True, 
         #height=800,
         #width=1200,           # Open in fullscreen
        resizable=False # Allow resizing
    )

    # Start the webview event loop
    webview.start()
