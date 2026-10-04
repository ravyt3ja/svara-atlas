# Exploration roadmap

This is a discovery-oriented starting point, not a commitment to one product
shape. Each phase should be informed by representative data and listening tests.

## 1. Curated listening set

- Collect a small, licensed or user-provided set of recordings and metadata.
- Include Telugu and Tamil film songs, Hindi cinema, English comparisons, and
  Carnatic examples; add other Indian and world languages without changing the
  core schema.
- Record what a person means by "similar" for each example: shared motif,
  performance, arrangement, lyrical theme, adaptation, or another relation.

## 2. Source adapters

- Choose the first source based on official API access and permitted metadata.
- Define identifier reconciliation and duplicate handling.
- Keep unavailable audio, lyrics, or language values explicitly unavailable;
  never infer them from an empty field.

## 3. Analysis experiments

- Compare pitch/motif representations that retain tonic and tuning context.
- Explore instrumentation, role, rhythmic-cycle, and production descriptors.
- Evaluate multilingual lyric analysis using consented or licensed text and
  human-reviewed labels; keep transliteration separate from translation.

## 4. Similarity and discovery

- Implement inspectable, dimension-specific comparisons before composite
  clustering.
- Let users choose a discovery lens, such as melodic resemblance or lyrical
  resonance, and explain why candidates were grouped.
- Test robustness across languages, genres, eras, and recording quality.

## 5. Product surfaces

Possible front ends include a command-line research tool, a personal listening
notebook, a web explorer, or a service embedded in a broader music application.
Keep the package core usable independently so these directions remain open.

## Open questions for later

- Which definition of "song" should lead: composition, recording, performance,
  film sequence, or a linked graph of these?
- What is the first permitted source of catalogue data and audio features?
- Should the initial result be nearest-neighbor discovery, explicit relation
  labels, or full clusters?
- Which listeners and domain experts can review cross-language and
  Carnatic/film-music judgments?
