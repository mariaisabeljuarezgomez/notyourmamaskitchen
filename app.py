from flask import Flask, send_from_directory, abort, request, jsonify
import os
import json
import shutil
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "menu_data.json"
BACKUP_DIR = "backups"

def validate_schema(data):
    """Basic validation for menu data schema."""
    required_keys = ["zoom", "scroll", "elements"]
    if not all(k in data for k in required_keys):
        return False
    if not isinstance(data["elements"], list):
        return False
    return True

@app.route("/")
def index():
    # Ensure index.html exists before serving
    if not os.path.exists("index.html"):
        return "Critical Error: index.html not found. Please run build_app.py first.", 500
    return send_from_directory(".", "index.html")

@app.route("/api/menu", methods=["GET"])
def get_menu():
    if not os.path.exists(DATA_FILE):
        return jsonify({"elements": [], "zoom": 1, "scroll": {"x": 0, "y": 0}, "info": "initial"}), 200
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/menu", methods=["POST"])
def save_menu():
    data = request.json
    if not data or not validate_schema(data):
        return jsonify({"error": "Invalid schema"}), 400

    try:
        # 1. Create backups directory if not exists
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        # 2. Versioned Backup before overwrite
        if os.path.exists(DATA_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(BACKUP_DIR, f"menu_data_{timestamp}.json")
            shutil.copy2(DATA_FILE, backup_path)

        # 3. Atomic Save (Write to temp, then rename)
        temp_file = DATA_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        # Replace original file with temp file (atomic on POSIX, reasonably safe on Windows)
        os.replace(temp_file, DATA_FILE)
        
        return jsonify({"status": "success", "backup": f"menu_data_{timestamp}.json" if 'timestamp' in locals() else None}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<path:path>")
def static_proxy(path):
    # Serve other static files if they exist
    return send_from_directory(".", path)

if __name__ == "__main__":
    # Railway provides the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
