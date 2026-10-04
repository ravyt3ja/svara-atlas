"""Read public playlist metadata through the official YouTube Data API."""

import json
import re
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen


YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
PLAYLIST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,100}$")


class YouTubeAPIError(Exception):
    """An expected error returned while requesting playlist metadata."""


def extract_playlist_id(playlist_url: str) -> str:
    """Return a playlist ID from a YouTube playlist or watch URL."""
    parsed = urlparse(playlist_url.strip())
    hostname = (parsed.hostname or "").lower()
    allowed_hosts = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }
    if parsed.scheme not in {"http", "https"} or hostname not in allowed_hosts:
        raise ValueError("Enter a valid YouTube or YouTube Music playlist URL.")

    playlist_ids = parse_qs(parsed.query).get("list", [])
    if not playlist_ids or not PLAYLIST_ID_PATTERN.fullmatch(playlist_ids[0]):
        raise ValueError("The URL does not contain a valid YouTube playlist ID.")
    return playlist_ids[0]


def fetch_public_playlist(
    playlist_url: str,
    api_key: str,
    *,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """Fetch a playlist's public video titles and links using YouTube Data API."""
    if not api_key.strip():
        raise YouTubeAPIError(
            "Set the YOUTUBE_API_KEY environment variable to import playlists."
        )
    playlist_id = extract_playlist_id(playlist_url)
    tracks: List[Dict[str, str]] = []
    page_token: Optional[str] = None

    while True:
        query = {
            "part": "snippet,contentDetails",
            "maxResults": "50",
            "playlistId": playlist_id,
            "key": api_key,
        }
        if page_token:
            query["pageToken"] = page_token
        request_url = "{}?{}".format(YOUTUBE_API_URL, urlencode(query))

        try:
            with urlopen(request_url, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            try:
                error_payload = json.loads(error.read().decode("utf-8"))
                message = error_payload.get("error", {}).get("message")
            except (UnicodeDecodeError, json.JSONDecodeError):
                message = None
            detail = message or "YouTube rejected the playlist request."
            raise YouTubeAPIError(detail) from error
        except (URLError, TimeoutError) as error:
            raise YouTubeAPIError(
                "Could not reach YouTube. Check your connection and try again."
            ) from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise YouTubeAPIError("YouTube returned an unreadable response.") from error

        for item in payload.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("contentDetails", {}).get("videoId")
            if not video_id:
                continue
            tracks.append(
                {
                    "videoId": video_id,
                    "title": snippet.get("title") or "Untitled video",
                    "channel": snippet.get("videoOwnerChannelTitle") or "",
                    "url": "https://www.youtube.com/watch?v={}".format(video_id),
                }
            )

        page_token = payload.get("nextPageToken")
        if not page_token:
            return {"playlistId": playlist_id, "tracks": tracks}
