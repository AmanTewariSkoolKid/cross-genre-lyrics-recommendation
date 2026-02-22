
---

# Changelog

## v0.0.1 — Initial File Management

* Created project directory structure under `approot/`
* Established:

  * `data/raw`
  * `data/interim`
  * `data/processed`
  * `src/` modular structure
* Separated raw data from processed outputs
* Prepared environment for modular preprocessing pipeline

---

## v0.0.2 — Spotify Dataset Preprocessing Pipeline

Implemented full preprocessing pipeline for `songs_with_attributes_and_lyrics.csv`.

Pipeline includes:

* Load raw CSV from `data/raw/`
* Keep required columns:

  * id
  * name → renamed to title
  * artists → renamed to artist
  * lyrics
* Drop all audio feature columns
* Remove null lyrics
* Remove short lyrics (< 30 words)
* Filter English entries (ASCII heuristic)
* Normalize title and artist
* Remove duplicate rows
* Normalize lyrics
* Remove duplicate lyrics using hash comparison
* Remove extreme length outliers
* Save cleaned dataset to:
  `data/processed/spotify_clean.csv`

---

## v0.0.3 — Pathing Fix

* Fixed incorrect file path handling for Spotify 960k CSV
* Ensured correct raw → processed flow
* Stabilized dataset loading logic

---

## v0.0.4 — Schema Normalization & Deduplication Preparation

Restructured dataset to support reliable duplicate detection.

### Added Columns:

* `normalized_title`
* `normalized_artist`
* `normalized_lyrics` (temporary)

### Implemented:

* Artist cleaning:

  * Lowercased
  * Removed brackets and quotes
  * Normalized whitespace

* Title normalization:

  * Lowercased
  * Removed non-alphanumeric characters (except spaces)
  * Collapsed multiple spaces
  * Trimmed whitespace

* Lyrics cleaning:

  * Lowercased
  * Removed punctuation
  * Preserved line breaks

* Normalized lyrics:

  * Lowercased
  * Removed punctuation
  * Fully collapsed whitespace
  * Prepared for hash-based duplicate detection

### Reordered Columns To:

* id
* title
* artist
* normalized_title
* normalized_artist
* lyrics
* normalized_lyrics

No duplicate removal executed in this version.
This version prepares dataset for composite key and lyric hash deduplication.

---


## v0.0.5 — Streaming CLI + Notebook Runner

* Added memory-light two-pass streaming pipeline for full dataset processing in chunks
* Implemented Python CLI script at `src/preprocessing/spotify_preprocess.py`
* Added matching CLI-style notebook at `notebooks/spotify_preprocess_cli.ipynb` with:

  * Structured PASS1/PASS2 logs
  * Configurable CHUNK_SIZE
  * Configurable paths

* Preserved full cleaning and deduplication logic:

  * Title/artist normalization
  * ASCII filter
  * Minimum word threshold
  * Composite-key deduplication
  * Lyrics-hash deduplication
  * IQR-based word-count filtering

* Auto-detects approot and applies default raw/processed paths
* Produces single consolidated `spotify_clean.csv` output to `data/processed`

** depcreated 'spotify960k_preprocessing' into  spotify960k_preprocessing_oldDeprecrated'use to performance issues.


