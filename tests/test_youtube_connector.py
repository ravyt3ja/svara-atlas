import json
import unittest
from io import BytesIO
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from svara_atlas.connectors.youtube import (
    YouTubeAPIError,
    extract_playlist_id,
    fetch_public_playlist,
)


class FakeResponse:
    def __init__(self, payload):
        self.content = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.content


class YouTubeConnectorTests(unittest.TestCase):
    def test_extracts_playlist_ids_from_youtube_and_music_urls(self):
        self.assertEqual(
            extract_playlist_id("https://www.youtube.com/playlist?list=PL_test-123"),
            "PL_test-123",
        )
        self.assertEqual(
            extract_playlist_id(
                "https://music.youtube.com/watch?v=video&list=PL_music"
            ),
            "PL_music",
        )

    def test_rejects_non_youtube_urls_and_missing_playlist_ids(self):
        for url in (
            "https://example.com/playlist?list=PL_test",
            "https://youtube.com/watch?v=video",
            "javascript://youtube.com/playlist?list=PL_test",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                extract_playlist_id(url)

    def test_fetches_all_pages_and_skips_removed_videos(self):
        responses = [
            FakeResponse(
                {
                    "items": [
                        {
                            "contentDetails": {"videoId": "video-one"},
                            "snippet": {
                                "title": "First song",
                                "videoOwnerChannelTitle": "Singer",
                            },
                        },
                        {"contentDetails": {}, "snippet": {"title": "Deleted video"}},
                    ],
                    "nextPageToken": "next-page",
                }
            ),
            FakeResponse(
                {
                    "items": [
                        {
                            "contentDetails": {"videoId": "video-two"},
                            "snippet": {"title": "Second song"},
                        }
                    ]
                }
            ),
        ]

        with patch(
            "svara_atlas.connectors.youtube.urlopen", side_effect=responses
        ) as mocked_urlopen:
            result = fetch_public_playlist(
                "https://www.youtube.com/playlist?list=PL_test", "test-key"
            )

        self.assertEqual(result["playlistId"], "PL_test")
        self.assertEqual([track["title"] for track in result["tracks"]], [
            "First song",
            "Second song",
        ])
        self.assertEqual(result["tracks"][0]["channel"], "Singer")
        self.assertEqual(
            result["tracks"][1]["url"],
            "https://www.youtube.com/watch?v=video-two",
        )
        first_query = parse_qs(urlparse(mocked_urlopen.call_args_list[0][0][0]).query)
        second_query = parse_qs(urlparse(mocked_urlopen.call_args_list[1][0][0]).query)
        self.assertEqual(first_query["key"], ["test-key"])
        self.assertEqual(second_query["pageToken"], ["next-page"])

    def test_requires_api_key(self):
        with self.assertRaisesRegex(YouTubeAPIError, "YOUTUBE_API_KEY"):
            fetch_public_playlist(
                "https://www.youtube.com/playlist?list=PL_test", ""
            )

    def test_reports_youtube_api_error_message(self):
        body = BytesIO(
            json.dumps({"error": {"message": "API key is invalid."}}).encode("utf-8")
        )
        error = HTTPError(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            403,
            "Forbidden",
            {},
            body,
        )

        with patch("svara_atlas.connectors.youtube.urlopen", side_effect=error):
            with self.assertRaisesRegex(YouTubeAPIError, "API key is invalid"):
                fetch_public_playlist(
                    "https://www.youtube.com/playlist?list=PL_test", "test-key"
                )


if __name__ == "__main__":
    unittest.main()
