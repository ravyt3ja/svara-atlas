"""Typed feature groups for future analysis and similarity workflows."""

from dataclasses import dataclass
from math import isfinite
from typing import Optional

from svara_atlas.domain.models import Language


@dataclass(frozen=True)
class FeatureEvidence:
    """Provenance for an extracted or inferred feature."""

    method: str
    confidence: Optional[float] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.method.strip():
            raise ValueError("Feature method must not be empty")
        if self.confidence is not None and (
            not isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0
        ):
            raise ValueError("Confidence must be a finite value from 0 to 1")


@dataclass(frozen=True)
class VocalFeatures:
    """Voice and melody descriptors, retaining tonic-relative pitch context."""

    pitch_contour_cents: tuple[float, ...] = ()
    tonic_hz: Optional[float] = None
    melodic_motifs: tuple[str, ...] = ()
    ornamentation: tuple[str, ...] = ()
    evidence: Optional[FeatureEvidence] = None

    def __post_init__(self) -> None:
        if any(not isfinite(value) for value in self.pitch_contour_cents):
            raise ValueError("Pitch contour values must be finite")
        if self.tonic_hz is not None and (
            not isfinite(self.tonic_hz) or self.tonic_hz <= 0
        ):
            raise ValueError("Tonic frequency must be a finite positive number")


@dataclass(frozen=True)
class ArrangementFeatures:
    """Descriptors for instrumentation, musical roles, rhythm, and texture."""

    instruments: tuple[str, ...] = ()
    musical_roles: tuple[str, ...] = ()
    rhythmic_cycles: tuple[str, ...] = ()
    texture_tags: tuple[str, ...] = ()
    tempo_bpm: Optional[float] = None
    evidence: Optional[FeatureEvidence] = None

    def __post_init__(self) -> None:
        if self.tempo_bpm is not None and (
            not isfinite(self.tempo_bpm) or self.tempo_bpm <= 0
        ):
            raise ValueError("Tempo must be a finite positive number")


@dataclass(frozen=True)
class LyricFeatures:
    """Language-aware semantic descriptors without requiring lyric text storage."""

    languages: tuple[Language, ...] = ()
    themes: tuple[str, ...] = ()
    imagery: tuple[str, ...] = ()
    moods: tuple[str, ...] = ()
    narrative_functions: tuple[str, ...] = ()
    evidence: Optional[FeatureEvidence] = None
