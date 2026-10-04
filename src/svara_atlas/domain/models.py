"""Provider-neutral identities and descriptive metadata for music."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Optional


class Platform(str, Enum):
    """Known catalogue sources; OTHER keeps the model open to new providers."""

    APPLE_MUSIC = "apple_music"
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    OTHER = "other"


@dataclass(frozen=True)
class Language:
    """A BCP 47 language tag with optional human-readable and script labels."""

    tag: str
    name: Optional[str] = None
    script: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.tag.strip():
            raise ValueError("Language tag must not be empty")


@dataclass(frozen=True)
class SourceReference:
    """A provider-specific identifier for a work, recording, or other entity."""

    platform: Platform
    external_id: str
    url: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.external_id.strip():
            raise ValueError("External ID must not be empty")


@dataclass(frozen=True)
class MusicalWork:
    """A composition-level identity, distinct from any particular recording."""

    work_id: str
    canonical_title: str
    languages: tuple[Language, ...] = ()
    creators: tuple[str, ...] = ()
    traditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.work_id.strip():
            raise ValueError("Work ID must not be empty")
        if not self.canonical_title.strip():
            raise ValueError("Canonical title must not be empty")


@dataclass(frozen=True)
class TrackRecording:
    """A particular recording with zero or more links to external catalogues."""

    recording_id: str
    title: str
    source_references: tuple[SourceReference, ...] = ()
    languages: tuple[Language, ...] = ()
    duration_seconds: Optional[float] = None
    release_year: Optional[int] = None
    version_label: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.recording_id.strip():
            raise ValueError("Recording ID must not be empty")
        if not self.title.strip():
            raise ValueError("Recording title must not be empty")
        if self.duration_seconds is not None and (
            not isfinite(self.duration_seconds) or self.duration_seconds <= 0
        ):
            raise ValueError("Duration must be a finite positive number")
        if self.release_year is not None and not 1 <= self.release_year <= 9999:
            raise ValueError("Release year must be between 1 and 9999")
