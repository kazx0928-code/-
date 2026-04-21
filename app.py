from flask import Flask, render_template, request, jsonify, send_from_directory
import base64
import os
import json
from datetime import datetime

app = Flask(__name__)
UPLOAD_BASE = 'uploads'
os.makedirs(UPLOAD_BASE, exist_ok=True)


@app.route('/')
def index():
    return render_template('gps_photo.html')


@app.route('/save_photos', methods=['POST'])
def save_photos():
    data = request.get_json()
    if not data or 'photos' not in data:
        return jsonify({'error': 'No photos data'}), 400

    folder_name = data.get('folder_name') or datetime.now().strftime('session_%Y%m%d_%H%M%S')
    folder_path = os.path.join(UPLOAD_BASE, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    saved = []
    metadata_list = []

    for i, photo in enumerate(data['photos']):
        try:
            image_data = photo['image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)

            lat = photo.get('latitude', 'unknown')
            lon = photo.get('longitude', 'unknown')
            accuracy = photo.get('accuracy', 'unknown')
            timestamp = photo.get('timestamp', datetime.now().isoformat())
            filename = f'photo_{i+1:03d}.jpg'
            filepath = os.path.join(folder_path, filename)

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            meta = {
                'filename': filename,
                'latitude': lat,
                'longitude': lon,
                'accuracy': accuracy,
                'timestamp': timestamp,
                'index': i + 1
            }
            metadata_list.append(meta)
            saved.append(filename)
        except Exception as e:
            return jsonify({'error': f'Failed on photo {i+1}: {str(e)}'}), 500

    # Save metadata JSON in folder
    with open(os.path.join(folder_path, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'folder': folder_name,
            'created_at': datetime.now().isoformat(),
            'total': len(saved),
            'photos': metadata_list
        }, f, ensure_ascii=False, indent=2)

    return jsonify({
        'success': True,
        'folder': folder_name,
        'saved_count': len(saved),
        'files': saved
    })


@app.route('/folders', methods=['GET'])
def list_folders():
    folders = []
    if os.path.exists(UPLOAD_BASE):
        for name in sorted(os.listdir(UPLOAD_BASE), reverse=True):
            path = os.path.join(UPLOAD_BASE, name)
            if os.path.isdir(path):
                meta_path = os.path.join(path, 'metadata.json')
                count = len([f for f in os.listdir(path) if f.endswith('.jpg')])
                meta = {}
                if os.path.exists(meta_path):
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                folders.append({
                    'name': name,
                    'photo_count': count,
                    'created_at': meta.get('created_at', '')
                })
    return jsonify(folders)


@app.route('/uploads/<path:filepath>')
def serve_upload(filepath):
    return send_from_directory(UPLOAD_BASE, filepath)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
