# ALONE-CODER
import os
import re
import asyncio
import random
import aiohttp
from typing import Union
from py_yt import VideosSearch, Playlist
from AloneX import logger, config
from AloneX.helpers import Track, utils

DOWNLOAD_DIR = "downloads"

# ── SAYA API CONFIGURATION ────────────────────────────────────────────────────
# Primary download API — get key from @SayaApiBot on Telegram
API_URL = os.environ.get("SAYA_API_URL", "https://shnwaz.pro")
API_KEY = os.environ.get("SAYA_API_KEY", "SAYA-9F83")


# ─────────────────────────────────────────────────────────────────────────────
# SAYA API DOWNLOADER (Primary)
# ─────────────────────────────────────────────────────────────────────────────

async def _saya_download(video_id: str, video: bool = False) -> str | None:
    """Download via Saya API (primary)."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ext = "mp4" if video else "mp3"
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/download",
                params={
                    "url": video_id,
                    "type": "video" if video else "audio",
                    "api_key": API_KEY,
                },
                timeout=aiohttp.ClientTimeout(total=300 if not video else 600),
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Saya API returned {resp.status} for {video_id}")
                    return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception as e:
        logger.warning(f"Saya API download failed for {video_id}: {e}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None


# ─────────────────────────────────────────────────────────────────────────────
# YT-DLP DOWNLOADER (Fallback)
# ─────────────────────────────────────────────────────────────────────────────

def _build_ydl_opts(outtmpl: str, cookies: str | None, video: bool = False) -> dict:
    opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "retries": 5,
        "fragment_retries": 5,
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
        opts["format"] = (
            "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]"
            "/bestvideo[height<=720]+bestaudio"
            "/best[height<=720]"
            "/best"
        )
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
    """Fallback: download using yt-dlp."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ext = "mp4" if video else "mp3"
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", url)[:50]
    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_id}.{ext}")
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{safe_id}.%(ext)s")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    yt_url = f"https://www.youtube.com/watch?v={url}" if len(url) == 11 else url

    def _do_download(fmt_override: str | None = None) -> bool:
        try:
            import yt_dlp
            opts = _build_ydl_opts(outtmpl, cookies, video)
            if fmt_override:
                opts["format"] = fmt_override
                opts.pop("postprocessors", None)
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([yt_url])
            return True
        except Exception as e:
            logger.warning(f"yt-dlp attempt failed ({fmt_override or 'default'}): {e}")
            return False

    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(None, _do_download)
    if not ok:
        logger.info("yt-dlp retrying with format=best")
        ok = await loop.run_in_executor(None, _do_download, "best")
    if not ok:
        return None

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path
    try:
        for f in os.listdir(DOWNLOAD_DIR):
            full = os.path.join(DOWNLOAD_DIR, f)
            if f.startswith(safe_id) and os.path.getsize(full) > 0:
                return full
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# UNIFIED DOWNLOAD FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

async def download_song(link: str, cookies: str | None = None) -> str | None:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None
    # Primary: Saya API
    result = await _saya_download(video_id, video=False)
    if result:
        return result
    # Fallback: yt-dlp
    logger.info(f"Saya API failed for {video_id}, falling back to yt-dlp")
    return await _ytdlp_download(video_id, cookies, video=False)


async def download_video(link: str, cookies: str | None = None) -> str | None:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None
    # Primary: Saya API
    result = await _saya_download(video_id, video=True)
    if result:
        return result
    # Fallback: yt-dlp
    logger.info(f"Saya API failed for {video_id}, falling back to yt-dlp")
    return await _ytdlp_download(video_id, cookies, video=True)


# ─────────────────────────────────────────────────────────────────────────────
# YOUTUBE CLASS — AloneX bot interface
# ─────────────────────────────────────────────────────────────────────────────

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.cookie_dir = "AloneX/cookies"

    def get_cookies(self) -> str | None:
        if not os.path.exists(self.cookie_dir):
            return None
        cookie_files = [f for f in os.listdir(self.cookie_dir) if f.endswith(".txt")]
        if not cookie_files:
            return None
        return os.path.join(self.cookie_dir, random.choice(cookie_files))

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        if not os.path.exists(self.cookie_dir):
            os.makedirs(self.cookie_dir)
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(urls):
                path = f"{self.cookie_dir}/cookie_{i}.txt"
                link = (
                    "https://batbin.me/api/v2/paste/" + url.split("/")[-1]
                    if "batbin.me" in url
                    else url
                )
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
