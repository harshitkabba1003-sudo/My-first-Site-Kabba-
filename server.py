import os
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from yt_dlp import YoutubeDL

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing so your GitHub Pages frontend can talk to it safely
CORS(app)

@app.route('/api/cut-clip', methods=['POST'])
def cut_clip():
    data = request.json or {}
    video_url = data.get('youtube_url')
    start_sec = int(data.get('start', 0))
    end_sec = int(data.get('end', 10))

    if not video_url:
        return jsonify({"error": "Missing YouTube video link"}), 400

    output_filename = "downloaded_short.mp4"
    
    # Clean up any leftover video files from previous runs safely
    if os.path.exists(output_filename):
        os.remove(output_filename)

    # Configure yt-dlp to download and cut simultaneously using FFmpeg natively on the fly
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': output_filename,
        'force_keyframes_at_cuts': True,
        'external_downloader': 'ffmpeg',
        'external_downloader_args': {
            'ffmpeg_i': [
                '-ss', str(start_sec),
                '-to', str(end_sec)
            ]
        },
        'quiet': False
    }

    try:
        print(f"Starting extraction request: {video_url} from {start_sec}s to {end_sec}s")
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Verify the file was generated and return it straight to the web browser download manager
        if os.path.exists(output_filename):
            return send_file(output_filename, as_attachment=True, mimetype='video/mp4')
        else:
            return jsonify({"error": "Video slicing failed to create target asset file."}), 500

    except Exception as e:
        print(f"Processing Failure: {str(e)}")
        return jsonify({"error": f"Internal execution failure: {str(e)}"}), 500

if __name__ == '__main__':
    # Launch the download API microservice on port 5000 local loop
    app.run(host='127.0.0.1', port=5000, debug=True)