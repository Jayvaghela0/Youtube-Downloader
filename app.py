from flask import Flask, request, jsonify
import os
import yt_dlp
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Environment variables se API key aur JBVYT value fetch karein
API_KEY = os.getenv('YTJBV')
JBVYT = os.getenv('JBVYT')

def get_video_stream_url(video_url):
    """
    Playwright ke through YouTube video stream URL extract karein.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Headless mode mein browser chalayein
        page = browser.new_page()
        
        # YouTube video page par jaayein
        page.goto(video_url)
        
        # Network requests intercept karein
        video_stream_url = None
        def handle_request(request):
            nonlocal video_stream_url
            if 'googlevideo.com' in request.url:  # YouTube video stream URL identify karein
                video_stream_url = request.url
                print(f"Found video stream URL: {video_stream_url}")
        
        # Network requests ko listen karein
        page.on('request', handle_request)
        
        # 10 seconds wait karein taaki video stream URL capture ho sake
        page.wait_for_timeout(10000)
        browser.close()
        
        return video_stream_url

        @app.route('/') 
def home(): 
    return "Welcome to YouTube Downloader! Use/download? URL=YOUTUBE_URL to download videos. "

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        # Playwright ke through video stream URL extract karein
        video_stream_url = get_video_stream_url(video_url)
        if not video_stream_url:
            return jsonify({"error": "Could not extract video stream URL"}), 500

        # yt-dlp ke sath video download karein
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt',  # Cookie file ka path
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',  # User-Agent
            'headers': {
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_stream_url, download=False)
            video_title = info.get('title', 'video')
            video_url = info['url']
            return jsonify({"title": video_title, "url": video_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
