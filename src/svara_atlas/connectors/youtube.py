"""Read public playlist metadata through the official YouTube Data API."""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen


YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
PLAYLIST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
POPULAR_LANGUAGES: Tuple[Tuple[str, str, str], ...] = (
    ("te", "Telugu", "Telugu songs"),
    ("ta", "Tamil", "Tamil songs"),
    ("hi", "Hindi", "Hindi songs"),
    ("en", "English", "English songs"),
)
FILM_MARKERS = re.compile(
    r"\b(?:film|films|movie|movies|cinema|soundtrack|ost|motion picture)\b"
    r"|సినిమా|చిత్రం|திரைப்படம்|சினிமா|படத்திலிருந்து|फिल्म|मूवी|सिनेमा",
    re.IGNORECASE,
)


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

        payload = _youtube_get(request_url, timeout)

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


def _youtube_get(url: str, timeout: float) -> Dict[str, Any]:
    """Request a YouTube API JSON response and report provider errors clearly."""
    try:
        with urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            error_payload = json.loads(error.read().decode("utf-8"))
            message = error_payload.get("error", {}).get("message")
        except (UnicodeDecodeError, json.JSONDecodeError):
            message = None
        raise YouTubeAPIError(
            message or "YouTube rejected the request."
        ) from error
    except (URLError, TimeoutError) as error:
        raise YouTubeAPIError(
            "Could not reach YouTube. Check your connection and try again."
        ) from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise YouTubeAPIError("YouTube returned an unreadable response.") from error

    if not isinstance(payload, dict):
        raise YouTubeAPIError("YouTube returned an unexpected response.")
    return payload


def _is_film_associated(video: Dict[str, Any]) -> bool:
    """Conservatively exclude entries whose metadata signals a film soundtrack."""
    snippet = video.get("snippet", {})
    text = " ".join(
        (
            snippet.get("title", ""),
            snippet.get("description", ""),
            snippet.get("channelTitle", ""),
        )
    )
    return bool(FILM_MARKERS.search(text))


def discover_popular_songs(
    api_key: str,
    *,
    limit_per_language: int = 100,
    max_search_pages: int = 5,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """Find view-ranked YouTube music-video candidates for four languages.

    YouTube search does not provide a canonical song chart or original film
    release-year metadata. Film-associated results are therefore excluded
    instead of treating upload dates as release years.
    """
    if not api_key.strip():
        raise YouTubeAPIError(
            "Set the YOUTUBE_API_KEY environment variable to discover songs."
        )
    if not 1 <= limit_per_language <= 100:
        raise ValueError("The per-language result limit must be from 1 to 100.")
    if not 1 <= max_search_pages <= 10:
        raise ValueError("The search page limit must be from 1 to 10.")

    results: Dict[str, Any] = {}
    for language_tag, language_name, query_text in POPULAR_LANGUAGES:
        candidates: Dict[str, Dict[str, Any]] = {}
        page_token: Optional[str] = None

        for _ in range(max_search_pages):
            params = {
                "part": "snippet",
                "type": "video",
                "videoCategoryId": "10",
                "order": "viewCount",
                "relevanceLanguage": language_tag,
                "maxResults": "50",
                "q": query_text,
                "key": api_key,
            }
            if page_token:
                params["pageToken"] = page_token
            search_payload = _youtube_get(
                "{}?{}".format(YOUTUBE_SEARCH_URL, urlencode(params)), timeout
            )
            video_ids = []
            for item in search_payload.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                if video_id and video_id not in candidates:
                    video_ids.append(video_id)
                    candidates[video_id] = {
                        "videoId": video_id,
                        "title": item.get("snippet", {}).get("title") or "Untitled video",
                        "channel": item.get("snippet", {}).get("channelTitle") or "",
                        "url": "https://www.youtube.com/watch?v={}".format(video_id),
                        "language": language_name,
                        "languageTag": language_tag,
                        "viewCount": 0,
                        "category": language_name,
                        "automatic": True,
                    }

            for index in range(0, len(video_ids), 50):
                batch = video_ids[index : index + 50]
                details_params = {
                    "part": "snippet,statistics",
                    "id": ",".join(batch),
                    "key": api_key,
                }
                details_payload = _youtube_get(
                    "{}?{}".format(YOUTUBE_VIDEOS_URL, urlencode(details_params)),
                    timeout,
                )
                returned_ids = set()
                for video in details_payload.get("items", []):
                    video_id = video.get("id")
                    if video_id:
                        returned_ids.add(video_id)
                    if _is_film_associated(video):
                        candidates.pop(video_id or "", None)
                        continue
                    if video_id not in candidates:
                        continue
                    snippet = video.get("snippet", {})
                    candidates[video_id]["title"] = (
                        snippet.get("title") or candidates[video_id]["title"]
                    )
                    candidates[video_id]["channel"] = (
                        snippet.get("channelTitle")
                        or candidates[video_id]["channel"]
                    )
                    candidates[video_id]["viewCount"] = int(
                        video.get("statistics", {}).get("viewCount", 0)
                    )
                for video_id in batch:
                    if video_id not in returned_ids:
                        candidates.pop(video_id, None)

            page_token = search_payload.get("nextPageToken")
            ranked = sorted(
                candidates.values(),
                key=lambda track: track["viewCount"],
                reverse=True,
            )
            if len(ranked) >= limit_per_language or not page_token:
                break

        ranked = sorted(
            candidates.values(),
            key=lambda track: track["viewCount"],
            reverse=True,
        )[:limit_per_language]
        results[language_name] = ranked

    return {
        "languages": [name for _, name, _ in POPULAR_LANGUAGES],
        "songsByLanguage": results,
        "limitPerLanguage": limit_per_language,
        "ranking": "YouTube view-ranked music-video search results; estimates, not official charts",
        "filmPolicy": (
            "Entries with film-related metadata markers are excluded because "
            "YouTube does not provide verified original film release years."
        ),
    }
