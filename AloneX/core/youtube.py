# ALONE-CODER
import os
import re
import asyncio
import random
import aiohttp
from py_yt import VideosSearch, Playlist
from AloneX import logger, config
from AloneX.helpers import Track, utils

DOWNLOAD_DIR = "downloads"


def _build_ydl_opts(file_path: str, cookies: str | None, video: bool = False) -> dict:
    opts = {
        "outtmpl": file_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "retries": 3,
        "socket_timeout": 30,
        "source_address": "0.0.0.0",
        "geo_bypass": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        },
    }
    if cookies:
        opts["cookiefile"] = cookies
    if video:
        opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]"
        opts["merge_output_format"] = "mp4"
    else:
        opts["format"] = "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ]
    return opts


async def _ytdlp_download(url: str, cookies: str | None, video: bool = False) -> str | None:
    """Download using yt-dlp in a thread pool executor."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ext = "mp4" if video else "mp3"
    # Derive a safe filename from the URL
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", url)[:50]
    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_id}.{ext}")
    # outtmpl without extension — yt-dlp adds it
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{safe_id}.%(ext)s")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    opts = _build_ydl_opts(outtmpl, cookies, video)

    def _do_download():
        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={url}" if len(url) == 11 else url])
        except Exception as e:
            logger.error(f"yt-dlp download error: {e}")
            return False
        return True

    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(None, _do_download)

    if not ok:
        return None

    # Find the downloaded file (yt-dlp may rename it)
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    # Scan directory for recently created file with matching prefix
    try:
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(safe_id) and os.path.getsize(os.path.join(DOWNLOAD_DIR, f)) > 0:
                return os.path.join(DOWNLOAD_DIR, f)
    except Exception:
        pass

    return None


async def download_song(link: str, cookies: str | None = None) -> str | None:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None
    return await _ytdlp_download(video_id, cookies, video=False)


async def download_video(link: str, cookies: str | None = None) -> str | None:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None
    return await _ytdlp_download(video_id, cookies, video=True)


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.cookie_dir = "AloneX/cookies"

    def get_cookies(self):
        if not os.path.exists(self.cookie_dir):
            return None
        cookies_files = [f for f in os.listdir(self.cookie_dir) if f.endswith(".txt")]
        if not cookies_files:
            return None
        return os.path.join(self.cookie_dir, random.choice(cookies_files))

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        if not os.path.exists(self.cookie_dir):
            os.makedirs(self.cookie_dir)
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(urls):
                path = f"{self.cookie_dir}/cookie_{i}.txt"
                if "batbin.me" in url:
                    link = "https://batbin.me/api/v2/paste/" + url.split("/")[-1]
                else:
                    link = url
                try:
                    async with session.get(link) as resp:
                        resp.raise_for_status()
                        with open(path, "wb") as fw:
                            fw.write(await resp.read())
                except Exception as e:
                    logger.error(f"Failed to download cookie from {url}: {e}")
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
            if results and results["result"]:
                data = results["result"][0]
                return Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name"),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")) if data.get("duration") else 0,
                    message_id=m_id,
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                    url=data.get("link"),
                    view_count=data.get("viewCount", {}).get("short"),
                    video=video,
                )
        except Exception as e:
            logger.error(f"Search error: {e}")
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist.get("videos", [])[:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")) if data.get("duration") else 0,
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception as e:
            logger.error(f"Playlist error: {e}")
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id or len(video_id) < 3:
            return None
        cookies = self.get_cookies()
        if video:
            return await download_video(video_id, cookies)
        else:
            return await download_song(video_id, cookies)
