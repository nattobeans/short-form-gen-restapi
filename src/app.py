import os, sys
from dotenv import load_dotenv

load_dotenv()


from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, select
from pytubefix import YouTube

from db.models import Video, Clip
from db.db_engine import create_db_and_tables, engine

app = FastAPI()
create_db_and_tables()
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Video Maker"}


def youtube_downloader(yt: YouTube, filename: str):
    try:
        yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=os.environ.get("VIDEO_BUCKET", "$HOME/Desktop"), max_retries=3, filename=f"{filename}-video.mp4")
        captions = yt.captions.get_by_language_code('en').generate_srt_captions()
        with open(f"{os.environ.get("TRANSCRIPT_BUCKET",  "$HOME/Desktop")}/{filename}-captions.txt", "w") as file:
            file.write(captions)
        return True
    except Exception as e:
        print(f"Download Video Failed: {e}")
        return False


@app.post("/video/")
def create_video(video: Video):
    if "youtube.com" in video.url:
        yt = YouTube(video.url)
        res = youtube_downloader(yt, video.name)

        if res:
            video.location = f"{os.environ.get("VIDEO_BUCKET",  "$HOME/Desktop")}/{video.name}-captions.mp4"
            video.transcript = f"{os.environ.get("TRANSCRIPT_BUCKET",  "$HOME/Desktop")}/{video.name}-captions.txt"

        else:
            return {"failed": "failed"}
    return {"message": "Done"}

