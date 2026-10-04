# Architecture

SvaraAtlas separates source identity, musical works, recordings, analysis, and
similarity so new use cases can be added without binding the core to a single
platform or interface.

## Main boundaries

- **Domain** (`src/svara_atlas/domain/`): provider-neutral identities and
  structured vocal, arrangement, and lyric descriptors.
- **Connectors** (`src/svara_atlas/connectors/`): read-only adapters that map
  approved sources into core models.
- **Analysis** (`src/svara_atlas/analysis/`): extraction and interpretation
  workflows, with provenance represented by `FeatureEvidence`.
- **Clustering** (`src/svara_atlas/clustering/`): future strategies that compare
  selected feature dimensions and preserve the reason for each relationship.

## Identity model

A `MusicalWork` represents a composition; a `TrackRecording` represents one
performance or recording; `SourceReference` represents a provider's catalogue
entry. One recording may have references on multiple platforms. Works and
recordings are not forcibly equated: cover, translation, adaptation, and
performance relationships need explicit modeling before they can be treated as
the same entity.

Language metadata uses open BCP 47 tags and optional script labels. There is no
language allowlist, and a work or recording may have multiple languages.

## AI boundary

Known identifiers, exact metadata lookups, feature transforms, and clustering
execution should remain ordinary code. A future TypeSafe integration can
contribute bounded semantic judgments, for example whether two multilingual
descriptions express a similar theme or narrative function. Keep the input
state, question meaning, candidate coverage, evidence, and raw probabilities
available for evaluation; do not treat a typed answer as ground truth.

The first version has no TypeSafe dependency, credential handling, or outbound
AI calls. Any service integration should be a separately testable adapter with
credentials kept outside the repository.
