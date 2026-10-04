# Analysis

Future analysis modules can extract melody and vocal contours, identify
instrumentation and arrangement, and produce language-aware lyric descriptors.
Keep extracted features separate from raw source material and attach provenance
through `FeatureEvidence`.

For Indian classical and film-music use cases, avoid flattening musical concepts
into Western-only labels. Preserve tonic-relative contours, ornamentation,
rhythmic cycles, and user/domain vocabulary alongside any normalized features.
Do not assume a raga, tala, note system, or translation is known when it has not
been established.

No audio, speech, lyrics, or external AI service is processed by this scaffold.
