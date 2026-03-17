
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

* Auto-detects repository root (formerly `approot`) and applies default raw/processed paths
* Produces single consolidated `spotify_clean.csv` output to `data/processed`

** depcreated 'spotify960k_preprocessing' into  spotify960k_preprocessing_oldDeprecrated'use to performance issues.


## v0.0.5.1 - improved explaination of preprocessing
    * title does it
Use this instead of the previous TLDR block.

---



## v0.0.5 — Feature Extraction Pipeline Initialization

* Created initial feature extraction module:
  `src/features/extract_features.py`
* Implemented dataset loading from
  `data/processed/spotify_clean.csv`
* Added validation for required columns:

  * id
  * title
  * artist
  * lyrics
* Removed rows with missing lyrics.
* Introduced helper column:

```text
_word_count
```

* `_word_count` stores the number of words per song using whitespace tokenization.
* Added dataset diagnostics output:

  * total songs loaded
  * average lyric word count
  * minimum lyric word count
  * maximum lyric word count
* Structured the module to support upcoming feature extraction functions:

  * lexical feature extraction
  * structural feature extraction
  * emotion feature extraction

This patch initializes the feature engineering stage and prepares the dataset for numerical feature generation used in clustering.

---

## v0.0.6 — Lexical Feature Extraction

Implemented lexical feature extraction in `src/features/extract_features.py`.

Added computed features:

* `unique_words`

* `lexical_diversity`

* `top_word_frequency`

* `repetition_score`

Features are derived using word tokenization and frequency counts. The module integrates `extract_lexical_features(df)` into the pipeline and prints diagnostics reporting average lexical diversity, average repetition score, and average vocabulary size. The dataset now contains initial numerical features for lyric pattern representation.


testing connection