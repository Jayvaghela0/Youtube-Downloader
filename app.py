from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # For CORS support
import os
import yt_dlp
import threading
import time
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Folder to store downloaded videos
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# List of user-agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
]

# Function to delete video after a delay
def delete_video_after_delay(video_path, delay=120):
    time.sleep(delay)
    if os.path.exists(video_path):
        os.remove(video_path)

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is required"}), 400

    # Randomly select a user-agent
    user_agent = random.choice(USER_AGENTS)

    # yt-dlp options with rotating user-agent
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'user-agent': user_agent,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
            video_path = os.path.join(DOWNLOAD_FOLDER, video_filename)

            # Schedule the video to be deleted after 2 minutes
            threading.Thread(target=delete_video_after_delay, args=(video_path, 120)).start()

            # Serve the video file for download
            return send_file(video_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
