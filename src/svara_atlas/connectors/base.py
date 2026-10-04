"""Interfaces for external catalogue adapters."""

from collections.abc import Sequence
from typing import Protocol

from svara_atlas.domain.models import Language, TrackRecording


class CatalogueConnector(Protocol):
    """A read-only provider adapter that maps external metadata to core models."""

    @property
    def platform_name(self) -> str:
        """Return a stable identifier for this connector."""
        ...

    def search_tracks(
        self,
        query: str,
        *,
        languages: Sequence[Language] = (),
        limit: int = 20,
    ) -> Sequence[TrackRecording]:
        """Search provider metadata without downloading audio or lyrics."""
        ...
