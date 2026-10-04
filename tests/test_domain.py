import unittest

from svara_atlas.domain.features import (
    ArrangementFeatures,
    FeatureEvidence,
    LyricFeatures,
    VocalFeatures,
)
from svara_atlas.domain.models import (
    Language,
    MusicalWork,
    Platform,
    SourceReference,
    TrackRecording,
)


class DomainModelTests(unittest.TestCase):
    def test_language_tags_are_open_to_multiple_languages_and_scripts(self) -> None:
        languages = (
            Language(tag="te", name="Telugu", script="Telu"),
            Language(tag="ta", name="Tamil", script="Taml"),
            Language(tag="hi", name="Hindi", script="Deva"),
            Language(tag="en", name="English", script="Latn"),
        )
        work = MusicalWork(
            work_id="work-1",
            canonical_title="A multilingual work",
            languages=languages,
            traditions=("Indian film music",),
        )

        self.assertEqual(tuple(language.tag for language in work.languages), (
            "te",
            "ta",
            "hi",
            "en",
        ))

    def test_recording_can_reference_multiple_catalogues(self) -> None:
        recording = TrackRecording(
            recording_id="recording-1",
            title="Demo recording",
            source_references=(
                SourceReference(Platform.SPOTIFY, "spotify-id"),
                SourceReference(Platform.YOUTUBE_MUSIC, "youtube-id"),
            ),
            duration_seconds=184.5,
        )

        self.assertEqual(len(recording.source_references), 2)

    def test_feature_groups_represent_independent_similarity_dimensions(self) -> None:
        evidence = FeatureEvidence(method="human-reviewed", confidence=0.9)
        features = (
            VocalFeatures(
                pitch_contour_cents=(0.0, 200.0, 300.0),
                tonic_hz=220.0,
                evidence=evidence,
            ),
            ArrangementFeatures(
                instruments=("veena", "mridangam"),
                rhythmic_cycles=("adi tala",),
            ),
            LyricFeatures(
                languages=(Language(tag="te", name="Telugu", script="Telu"),),
                themes=("longing",),
            ),
        )

        self.assertEqual(len(features), 3)

    def test_invalid_duration_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duration"):
            TrackRecording(
                recording_id="recording-1",
                title="Invalid recording",
                duration_seconds=0,
            )

    def test_invalid_evidence_confidence_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Confidence"):
            FeatureEvidence(method="unreviewed", confidence=1.1)


if __name__ == "__main__":
    unittest.main()
