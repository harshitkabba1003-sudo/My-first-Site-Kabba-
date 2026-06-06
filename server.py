import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so your GitHub Pages site can securely communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/cut")
async def cut_video(url: str, start: int, end: int):
    raw_output = "raw_full_video.mp4"
    sliced_output = "viral_short_clip.mp4"
    
    # Reset old file instances before starting a new download run
    if os.path.exists(raw_output): os.remove(raw_output)
    if os.path.exists(sliced_output): os.remove(sliced_output)
        
    try:
        print(f"📥 Fetching video stream payload for: {url}")
        # Command line parameters for high-speed download streams via yt-dlp
        download_command = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "-o", raw_output,
            url
        ]
        subprocess.run(download_command, check=True)
        
        print(f"✂️ Slicing video frame window: {start}s to {end}s")
        duration = end - start
        
        # Fast multi-threaded rendering command using native system FFmpeg
        ffmpeg_command = [
            "ffmpeg",
            "-ss", str(start),
            "-i", raw_output,
            "-t", str(duration),
            "-c:v", "copy", "-c:a", "copy",
            sliced_output
        ]
        subprocess.run(ffmpeg_command, check=True)
        
        # Remove the large raw video to save hard drive storage space
        if os.path.exists(raw_output):
            os.remove(raw_output)
            
        # Deliver the trimmed video clip straight back to your browser window
        return FileResponse(path=sliced_output, media_type="video/mp4", filename=sliced_output)
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Internal Engine Error: {str(error)}")

if __name__ == "__main__":
    import uvicorn
    # Listen locally on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
