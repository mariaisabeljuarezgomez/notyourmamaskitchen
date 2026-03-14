from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Ensure index.html exists before serving
    if not os.path.exists("index.html"):
        return "Critical Error: index.html not found. Please run build_app.py first.", 500
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    # Serve other static files if they exist (though most are embedded)
    return send_from_directory(".", path)

if __name__ == "__main__":
    # Railway provides the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
