import os, sys
from dotenv import load_dotenv
from pathlib import Path
from enum import Enum

load_dotenv()


from fastapi import Depends, FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from sqlmodel import Field, Session, SQLModel, select
from pytubefix import YouTube

from db.models import Video, Clip
from db.db_engine import create_db_and_tables, engine, supabase


class BUCKET(Enum):
    TRANSCRIPTS = "transcripts"
    VIDEOS = "videos"


class TEMP(Enum):
    TRANSCRIPTS = Path(f"{os.environ.get("TRANSCRIPT_TEMP",  "$HOME/Desktop")}")
    VIDEOS = Path(f"{os.environ.get("VIDEO_TEMP",  "$HOME/Desktop")}")

class EXT(Enum):
    TRANSCRIPT = "captions.txt"
    VIDEO = "video.mp4"

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Video Maker"}


def youtube_downloader(yt: YouTube, filename: str):
    """
    Downloads video from youtube using supplied link from user
        - Video must have captions
        - Video must be an old combined format for now
    """
    
    # The first get captions call is the current standard. 
    # Some links only work on the old standard (elif statement) so both need to be used
    captions = None
    if yt.captions["a.en"]:
        captions = yt.captions["a.en"].generate_srt_captions()
    elif yt.captions.get_by_language_code("en"):
        captions = yt.captions.get_by_language_code("en").generate_srt_captions()
    if not captions:
        raise Exception("Video has no english Captions")

    transcript_filepath = Path(TEMP.TRANSCRIPTS.value, f"{filename}-{EXT.TRANSCRIPT.value}")
    with open(transcript_filepath, "w") as file:
        file.write(captions)

    if not transcript_filepath.exists():
        raise Exception("Transcripts failed to write")

    video_filename = f"{filename}-{EXT.VIDEO.value}"
    video_filepath = Path(TEMP.VIDEOS.value, video_filename)
    yt.streams.filter(progressive=True, file_extension="mp4").order_by(
        "resolution"
    ).desc().first().download(
        output_path=TEMP.VIDEOS.value,
        max_retries=3,
        filename=video_filename,
    )
    if not video_filepath.exists():
        raise Exception(f"Failed to Download Video: {video_filename}")


def upload_to_bucket(filename: str):
    """
    Uploads the downloaded youtube files to supabase buckets
        - transcripts <.txt>
        - videos <.mp4>
    """

    # Uploads transcript. Supabase itself will check if file exists and throw already exists error
    transcript_filename = f"{filename}-{EXT.TRANSCRIPT.value}"
    transcript_filepath = Path(TEMP.TRANSCRIPTS.value, transcript_filename)
    response = supabase.storage.from_(BUCKET.TRANSCRIPTS.value).upload(
        transcript_filename,
        transcript_filepath,
        {
            "content-type": "text/plain",
        },
    )

    # Checks transcript uploaded successfully
    response = supabase.storage.from_(BUCKET.TRANSCRIPTS.value).get_public_url(transcript_filename)
    if not response:
        raise Exception("Failed to upload transcript to bucket")

    # Uploads video. Supabase itself will check if video exists and throw already exists error
    video_filename = f"{filename}-{EXT.VIDEO.value}"
    video_filepath = Path(TEMP.VIDEOS.value, video_filename)
    response = supabase.storage.from_(BUCKET.VIDEOS.value).upload(
        video_filename,
        video_filepath,
        {
            "content-type": "video/mp4",
        },
    )

    # Checks video uploaded successfully
    response = supabase.storage.from_(BUCKET.VIDEOS.value).get_public_url(video_filename)
    if not response:
        raise Exception("Failed to upload transcript to bucket")
    

@app.post("/video/")
def create_video(video: Video):
    try:
        if "youtube.com" in video.url:
            yt = YouTube(video.url)
            res = youtube_downloader(yt, video.name)
            upload_to_bucket(video.name)

        return {"message": "Done"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
