import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from core.dispatcher import Dispatcher

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

PROJECT_ROOT = "/home/usic/.gemini/antigravity/scratch/autobot"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "data")
dispatcher = Dispatcher(PROJECT_ROOT)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/media/<path:filename>')
def serve_media(filename):
    from flask import send_from_directory
    return send_from_directory(MEDIA_ROOT, filename)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    queue_file = os.path.join(PROJECT_ROOT, "data/pipeline_queue.json")
    if os.path.exists(queue_file):
        with open(queue_file, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    accounts_file = os.path.join(PROJECT_ROOT, "data/accounts.json")
    if os.path.exists(accounts_file):
        with open(accounts_file, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/tasks/approve/<int:task_id>', methods=['POST'])
def approve_task(task_id):
    dispatcher.approve_task(task_id)
    return jsonify({"status": "success"})

@app.route('/api/tasks/add', methods=['POST'])
def add_task():
    data = request.json
    task_type = data.get('type')
    task_data = data.get('data')
    account_id = data.get('account_id')
    dispatcher.add_task(task_type, task_data, account_id=account_id)
    return jsonify({"status": "success"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Simple stats calculation
    queue_file = os.path.join(PROJECT_ROOT, "data/pipeline_queue.json")
    stats = {"pending": 0, "completed": 0, "failed": 0, "awaiting_approval": 0}
    if os.path.exists(queue_file):
        with open(queue_file, 'r') as f:
            queue = json.load(f)
            for t in queue:
                status = t.get('status')
                if status in stats:
                    stats[status] += 1
    return jsonify(stats)

@app.route('/api/assets', methods=['GET'])
def get_assets():
    assets = {
        "music": [],
        "images": [],
        "videos": []
    }
    
    music_dir = os.path.join(PROJECT_ROOT, "assets/music")
    image_dir = os.path.join(PROJECT_ROOT, "data/generated_images")
    video_dir = os.path.join(PROJECT_ROOT, "data/processed_video")
    
    if os.path.exists(music_dir):
        assets["music"] = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
    if os.path.exists(image_dir):
        assets["images"] = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg'))]
    if os.path.exists(video_dir):
        assets["videos"] = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.mov'))]
        
    return jsonify(assets)

@app.route('/api/assets/upload', methods=['POST'])
def upload_asset():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    asset_type = request.form.get('type', 'music')
    
    target_dir = os.path.join(PROJECT_ROOT, f"assets/{asset_type}")
    if asset_type == 'images': target_dir = os.path.join(PROJECT_ROOT, "data/generated_images")
    
    os.makedirs(target_dir, exist_ok=True)
    file.save(os.path.join(target_dir, file.filename))
    return jsonify({"status": "success"})

@app.route('/api/generate/image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    char_name = data.get('character_name', 'AI_Model')
    
    # Добавляем задачу в очередь для VisualBot
    dispatcher.add_task("image_generation", {
        "prompt": prompt,
        "character_name": char_name
    })
    
    # Также запускаем бота в отдельном процессе для теста, чтобы не ждать
    import subprocess
    python_executable = os.path.join(PROJECT_ROOT, ".venv/bin/python3")
    subprocess.Popen([python_executable, os.path.join(PROJECT_ROOT, "bots/visual_bot/generator.py")])
    
    return jsonify({"status": "task_added"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
