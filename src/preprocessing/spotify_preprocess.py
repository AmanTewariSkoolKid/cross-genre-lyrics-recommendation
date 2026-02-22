"""Memory-light Spotify lyrics preprocessing.

Two-pass streaming pipeline that matches the notebook logic but runs as a CLI script.
- Pass 1: stream the raw CSV in chunks, clean rows, deduplicate on composite keys and lyric hash, collect word counts, and compute IQR bounds.
- Pass 2: stream again, reapply cleaning + dedup + word-count IQR filter, and write a single consolidated spotify_clean.csv.

Defaults mirror the notebook; override paths or chunk size via CLI flags.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from typing import Iterable, Tuple

import pandas as pd

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def ascii_ratio(text: str) -> float:
    if not isinstance(text, str) or len(text) == 0:
        return 0.0
    return sum(ord(c) < 128 for c in text) / len(text)


def normalize_meta(s: str) -> str:
    if not isinstance(s, str):
        return ''
    s = s.lower()
    s = re.sub(r"\([^)]*(live|remaster(ed)?).*?\)", '', s, flags=re.IGNORECASE)
    s = re.sub(r"[\-\u2013\u2014]\s*live\s*$", '', s, flags=re.IGNORECASE)
    s = re.sub(r"\([^)]*\)", '', s)
    s = re.sub(r"[^\w\s]", ' ', s)
    return re.sub(r"\s+", ' ', s).strip()


def normalize_title_strong(s: str) -> str:
    if not isinstance(s, str):
        return ''
    t = s.lower()
    t = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', t)
    t = re.sub(r'[^A-Za-z0-9 ]+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def normalize_title(s: str) -> str:
    if not isinstance(s, str):
        return ''
    t = s.lower()
    t = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', t)
    t = re.sub(r'[^A-Za-z0-9 ]+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def normalize_lyrics(text: str) -> str:
    if not isinstance(text, str):
        return ''
    t = text.lower()
    t = re.sub(r"[^\w\s']", ' ', t)
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in t.splitlines()]
    return '\n'.join(lines)


def md5_hash(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()


# -----------------------------------------------------------------------------
# Core processing
# -----------------------------------------------------------------------------

def detect_app_root(start: Path) -> Path:
    base = start
    if base.name == '.venv':
        base = base.parent
    if (base / 'approot').exists():
        return (base / 'approot').resolve()
    p = base
    for _ in range(6):
        if (p / 'approot').exists():
            return (p / 'approot').resolve()
        if p.parent == p:
            break
        p = p.parent
    return base.resolve()


def clean_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    chunk = chunk.rename(columns={'name': 'title', 'artists': 'artist'})
    chunk = chunk[chunk['lyrics'].notna()].copy()

    chunk['_word_count'] = chunk['lyrics'].astype(str).str.split().str.len()
    chunk = chunk[chunk['_word_count'] >= 30].copy()
    chunk['_ascii'] = chunk['lyrics'].astype(str).map(ascii_ratio)
    chunk = chunk[chunk['_ascii'] >= 0.90].copy()

    chunk['artist'] = chunk['artist'].astype(str).str.lower()
    chunk['artist'] = chunk['artist'].str.replace(r'\[|\]', '', regex=True)
    chunk['artist'] = chunk['artist'].str.replace("'", '', regex=False)
    chunk['artist'] = chunk['artist'].str.replace(r'\s+', ' ', regex=True).str.strip()

    chunk['title'] = chunk['title'].astype(str)
    chunk['normalized_title'] = chunk['title'].map(normalize_title_strong)

    chunk['normalized_artist'] = chunk['artist'].str.lower()
    chunk['normalized_artist'] = chunk['normalized_artist'].str.replace(r'[^A-Za-z0-9 ]+', ' ', regex=True)
    chunk['normalized_artist'] = chunk['normalized_artist'].str.replace(r'\s+', ' ', regex=True).str.strip()

    chunk['lyrics'] = chunk['lyrics'].astype(str).map(normalize_lyrics)

    chunk['normalized_lyrics'] = chunk['lyrics'].str.lower()
    chunk['normalized_lyrics'] = chunk['normalized_lyrics'].str.replace(r'[^\w\s]', ' ', regex=True)
    chunk['normalized_lyrics'] = chunk['normalized_lyrics'].str.replace(r'\s+', ' ', regex=True).str.strip()

    chunk['_comp_key'] = chunk['normalized_title'].fillna('') + '_' + chunk['normalized_artist'].fillna('')
    chunk['_lyrics_hash'] = chunk['lyrics'].map(md5_hash)
    return chunk


def pass1_compute_bounds(
    raw_csv: Path, chunk_size: int, usecols: Iterable[str]
) -> Tuple[int, int, int, int]:
    seen_comp_keys: set[str] = set()
    seen_lyrics_hash: set[str] = set()
    word_counts: list[int] = []
    rows_in = rows_kept = 0

    for i, chunk in enumerate(pd.read_csv(raw_csv, usecols=usecols, chunksize=chunk_size, low_memory=False)):
        rows_in += len(chunk)
        chunk = clean_chunk(chunk)
        mask_new = (~chunk['_comp_key'].isin(seen_comp_keys)) & (~chunk['_lyrics_hash'].isin(seen_lyrics_hash))
        chunk = chunk[mask_new]
        seen_comp_keys.update(chunk['_comp_key'])
        seen_lyrics_hash.update(chunk['_lyrics_hash'])
        word_counts.extend(chunk['_word_count'].astype(int).tolist())
        rows_kept += len(chunk)
        print(f'Pass1 chunk {i:03d}: kept {len(chunk):6d} / {rows_in:6d} so far')

    if not word_counts:
        raise RuntimeError('No rows survived initial filtering; check the raw CSV and filters.')

    wc_series = pd.Series(word_counts)
    q1, q3 = wc_series.quantile(0.25), wc_series.quantile(0.75)
    iqr = q3 - q1
    lo = max(1, int(q1 - 1.5 * iqr))
    hi = int(q3 + 1.5 * iqr)

    print(f'Pass1 complete: input {rows_in:,} → kept {rows_kept:,}. Word-count IQR [{lo}, {hi}].')
    return lo, hi, rows_in, rows_kept


def pass2_write_output(
    raw_csv: Path,
    out_csv: Path,
    chunk_size: int,
    usecols: Iterable[str],
    lo: int,
    hi: int,
) -> int:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if out_csv.exists():
        out_csv.unlink()

    seen_comp_keys: set[str] = set()
    seen_lyrics_hash: set[str] = set()
    rows_written = 0

    for i, chunk in enumerate(pd.read_csv(raw_csv, usecols=usecols, chunksize=chunk_size, low_memory=False)):
        chunk = clean_chunk(chunk)

        mask_new = (~chunk['_comp_key'].isin(seen_comp_keys)) & (~chunk['_lyrics_hash'].isin(seen_lyrics_hash))
        chunk = chunk[mask_new]
        seen_comp_keys.update(chunk['_comp_key'])
        seen_lyrics_hash.update(chunk['_lyrics_hash'])

        chunk = chunk[(chunk['_word_count'] >= lo) & (chunk['_word_count'] <= hi)].copy()

        out = chunk[['id', 'title', 'artist', 'normalized_title', 'normalized_artist', 'lyrics', 'normalized_lyrics']]
        mode = 'w' if rows_written == 0 else 'a'
        header = rows_written == 0
        out.to_csv(out_csv, mode=mode, header=header, index=False)

        rows_written += len(out)
        print(f'Pass2 chunk {i:03d}: wrote {len(out):6d} (total {rows_written:,})')

    print(f'✔ Done. Final rows written: {rows_written:,} → {out_csv}')
    return rows_written


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Memory-light Spotify preprocessing (two-pass streaming).')
    parser.add_argument('--chunk-size', type=int, default=50_000, help='Chunk size for streaming reads.')
    parser.add_argument('--input', type=Path, help='Path to raw songs_with_attributes_and_lyrics.csv.')
    parser.add_argument('--output', type=Path, help='Path to write spotify_clean.csv.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    app_root = detect_app_root(Path.cwd())
    default_raw = app_root / 'data' / 'raw' / 'songs_with_attributes_and_lyrics.csv'
    default_out = app_root / 'data' / 'processed' / 'spotify_clean.csv'

    raw_csv = args.input if args.input is not None else default_raw
    out_csv = args.output if args.output is not None else default_out

    if not raw_csv.exists():
        raise FileNotFoundError(f'Raw CSV not found at {raw_csv}')

    chunk_size = max(1_000, args.chunk_size)
    usecols = ['id', 'name', 'artists', 'lyrics']

    lo, hi, rows_in, rows_kept = pass1_compute_bounds(raw_csv, chunk_size, usecols)
    _ = pass2_write_output(raw_csv, out_csv, chunk_size, usecols, lo, hi)


if __name__ == '__main__':
    main()
