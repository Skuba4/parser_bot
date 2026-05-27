from yt_dlp import YoutubeDL
import os
import json
import hashlib
import ffmpeg
from pprint import pprint

CACHE_DIR = "downloads"
os.makedirs(CACHE_DIR, exist_ok=True)

MAX_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_CACHE_SIZE = 100 * 1024 * 1024 * 1024  # 100 GB
CLEANUP_STEP = 5 * 1024 * 1024 * 1024  # 5 GB


def get_video_metadata(path):
    try:
        probe = ffmpeg.probe(path)
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        format_info = probe.get('format', {})
        return {
            "duration": int(float(format_info.get("duration", 0))),
            "width": video_stream.get("width", 0) if video_stream else 0,
            "height": video_stream.get("height", 0) if video_stream else 0
        }
    except Exception as e:
        print(f"ffmpeg.probe error: {e}")
        return {"duration": 0, "width": 0, "height": 0}


def link_to_hash(link: str) -> str:
    """Создаёт криптографический хеш от строки.
    Он всегда одинаков для одной и той же ссылки (детерминированный)."""
    return hashlib.sha1(link.encode()).hexdigest()[:16]


def get_cache_size():
    return sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in os.listdir(CACHE_DIR))


def cleanup_cache():
    files = [os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR)]
    files = [(f, os.path.getctime(f), os.path.getsize(f)) for f in files]
    files.sort(key=lambda x: x[1])  # по времени создания

    total_removed = 0
    for f, _, size in files:
        os.remove(f)
        total_removed += size
        if total_removed >= CLEANUP_STEP:
            break


class FileTooLargeError(Exception):
    pass


def download(link: str):
    video_id = link_to_hash(link)
    video_file = os.path.join(CACHE_DIR, f"{video_id}.mp4")
    meta_file = os.path.join(CACHE_DIR, f"{video_id}.json")

    # Проверка кеша видео
    if os.path.exists(video_file ) and os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            info = json.load(f)
        return video_file , info

    # Проверка оставшегося места в кеше
    if get_cache_size() >= MAX_CACHE_SIZE:
        cleanup_cache()


    def stop_if_too_large(x):
        total = x.get('total_bytes') or x.get('total_bytes_estimate')
        if total and total > MAX_BYTES:
            raise FileTooLargeError(f"⚠️ Лимит Telegram 50MB. Видео весит {round(total / 1024 / 1024, 1)} MB")

        if x.get('status') == 'downloading':
            downloaded = x.get('downloaded_bytes', 0)
            if downloaded > MAX_BYTES:
                raise FileTooLargeError(
                    f"⚠️ Лимит Telegram 50MB. Превышение во время загрузки ({round(downloaded / 1024 / 1024, 1)} MB)")

    ydl_opts = {
        "outtmpl": video_file,
        "merge_output_format": "mp4",
        "quiet": True,
        "progress_hooks": [stop_if_too_large],
        "add_metadata": True,
        "embed_thumbnail": True,
        "postprocessor_args": ["-movflags", "faststart"],
        "format": "best"
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)

    meta = get_video_metadata(video_file)

    data = {
        "duration": meta["duration"],                   # продолжительность
        "width": meta["width"],                         # ширина
        "height": meta["height"],                       # высота
        "title": info.get("title"),                     # описание маленькое (YouTube)
        "fulltitle": info.get("fulltitle"),             # описание маленькое (YouTube)
        "description": info.get("description"),         # описание большое (YouTube)
        "uploader": info.get("uploader"),               # никнейм (не ютуб)
        "uploader_id": info.get("uploader_id"),         # @никнейм (YouTube)
        "uploader_url": info.get("uploader_url"),       # URL на канал (YouTube)
        "channel": info.get("channel"),                 # никнейм (не ютуб)
        'extractor_key': info.get("extractor_key"),     # платформа
    }

    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    # для отладки через консоль
    # pprint(info)                  # весь полученный JSON
    # print(data, flush=True)       # метаданные

    return video_file, data
