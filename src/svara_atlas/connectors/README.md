# Connectors

Connectors translate provider or dataset metadata into the provider-neutral
domain models. Keep provider-specific IDs and URLs in `SourceReference`; a
recording can be linked to multiple providers.

Use official APIs, licensed datasets, or explicit user-provided data, and honor
each source's terms. This package intentionally contains no scraping, audio
download, lyric harvesting, authentication flow, or provider SDK.
