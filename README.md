# SvaraAtlas

**A listening atlas for music across languages, traditions, and platforms.**

SvaraAtlas is an open-ended foundation for finding musical kinship between
recordings. It is especially curious about Telugu and Tamil film music, Hindi
cinema, Carnatic music, and the conversations they have with music from other
languages and traditions.

The long-term idea is to bring together several kinds of evidence:

- **Melody and voice:** pitch contours, motifs, ornamentation, and (where useful)
  swara or note interpretations that retain their tuning and tonic context.
- **Arrangement and rhythm:** instrumentation, musical roles, texture, rhythmic
  cycles, tempo, and production.
- **Lyrics and meaning:** language-aware themes, imagery, mood, narrative function,
  and cross-language relationships without treating translation as equivalence.
- **Context and discovery:** composers, lyricists, performers, film and album
  context, tradition, era, and user-curated connections.
- **Platform identity:** separate provider records for Spotify, Apple Music,
  YouTube, YouTube Music, and future sources, linked without making any one
  provider the canonical catalogue.

The project starts with domain models and clear seams between sources, analysis,
and future clustering strategies. It does not yet download or analyze audio, or
make similarity claims. Its YouTube connector fetches public catalogue metadata
only. Similarity choices should be tested against real,
appropriately licensed examples rather than hidden behind arbitrary thresholds.

## Design principles

1. **Many kinds of closeness.** A shared composition, a cover, a similar melodic
   phrase, a comparable arrangement, and a lyrical parallel are different
   relationships. Keep them distinguishable and let a listening task choose
   which matters.
2. **Language-aware, not language-limited.** Telugu, Tamil, Hindi, and English
   are first-class interests, not an exhaustive allowlist. Preserve language and
   script metadata, and leave room for transliteration and multilingual works.
3. **Evidence travels with an interpretation.** Future extracted or inferred
   features should record how they were produced and what they describe.
4. **Adapters, not platform lock-in.** Provider connectors belong at the edges;
   the core models do not depend on any provider SDK.
5. **Respect rights and access rules.** Use official APIs, licensed datasets,
   and user-provided material. Do not scrape platform audio or lyrics. Keep
   credentials server-side and out of source control.
6. **Open to other ideas.** The core is a Python package with separable modules,
   so it can later support a CLI, service, research workflow, or a larger
   application.

## Repository map

```text
svara-atlas/
├── data/
│   └── fixtures/       # Tiny, fictional examples for development
├── docs/
│   ├── architecture.md
│   └── roadmap.md
├── src/svara_atlas/
│   ├── analysis/       # Audio, music-theory, and language analysis seams
│   ├── clustering/    # Similarity and grouping strategies
│   ├── connectors/     # Platform and dataset adapters
│   └── domain/         # Provider-neutral music and feature models
└── tests/
```

## Getting started

Requires Python 3.9 or newer. The foundation has no runtime dependencies.

```sh
python -m unittest discover -s tests -v
```

For a development install:

```sh
python -m pip install -e ".[dev]"
```

## Automatically build popular-song lists

The local browser app can generate estimated lists for Telugu, Tamil, Hindi,
and English. It searches YouTube's Music video category ordered by view count,
fetches public video metadata, and groups results by the language search.
It can return up to 100 results per language, but may return fewer after
excluding entries whose metadata contains film-related markers. Results are
video-based estimates, not official or definitive song charts; language
relevance is not verified, and duplicates, covers, or unrelated videos may
remain. The metadata marker filter cannot reliably detect every film song.
YouTube does not provide an original film release year in these search
results, so upload dates are not treated as song or film release dates.

1. In Google Cloud Console, create an API key and enable **YouTube Data API v3**
   for its project. Restrict the key to that API.
2. Install and start the app:

   ```sh
   python -m pip install -e .
   YOUTUBE_API_KEY="your-api-key" svara-atlas-web
   ```

3. Open <http://127.0.0.1:8000> and click **Generate my lists**. The app
   automatically groups results into language lists. Select **Export CSV** to
   download them.

The API key is read only by the local server and is never sent to the browser.
Keep it private and do not commit it. Private playlists and account sign-in
aren't supported. By default, the server listens only on your own computer;
do not expose it to the public internet without adding authentication and
appropriate production hosting.

Results and categories are saved in this browser's local storage. The optional
playlist import is still available below the automatic discovery section.

## TypeSafe and semantic analysis

Cross-language lyric interpretation is a good candidate for small, explicit
semantic judgments, such as identifying themes or deciding whether two
descriptions express a similar narrative function. If/when that integration is
added, code should own retrieval, normalization, and clustering while typed
judgments supply bounded interpretations. Keep original evidence, language,
question meaning, and uncertainty available; evaluate decisions on a curated,
multilingual set before using them to group real music.

The initial scaffold deliberately does not call an AI service or require an API
key. See [the architecture notes](docs/architecture.md) and
[the roadmap](docs/roadmap.md) for likely next steps.
