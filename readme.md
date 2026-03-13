# Lyrics-Based Music Recommendation System

**Unsupervised Pattern Recognition Approach**

---

## Project Overview

This project develops a lyrics-driven music recommendation system using unsupervised machine learning and structured pattern recognition techniques.

Unlike conventional systems that rely on user behavior, audio features, or genre classification, this model focuses exclusively on measurable lyrical characteristics. Songs are grouped based on structural and lexical patterns derived from their lyrics, enabling cross-genre recommendation based purely on textual similarity.

The system emphasizes interpretability, modular design, and academic defensibility.

---

## Objectives

* Build a lyrics-only recommendation framework
* Extract structured numerical features from song lyrics
* Apply unsupervised clustering to identify natural similarity groups
* Generate recommendations using distance-based similarity
* Maintain explainability and reproducibility

---

## Methodology

The system follows a structured pipeline:

1. **Data Ingestion**
   Load structured lyric dataset (CSV format).

2. **Preprocessing**

   * Filter English lyrics
   * Remove null or corrupted entries
   * Normalize title and artist fields
   * Remove duplicate songs
   * Clean lyrical text while preserving structural properties

3. **Feature Engineering**
   Extract numeric features including:

   * Total word count
   * Unique word count
   * Lexical diversity ratio
   * Repetition metrics
   * Line structure statistics
   * Emotion keyword density

4. **Vector Representation & Scaling**
   Convert each song into a normalized numeric feature vector.

5. **Clustering**
   Apply K-Means clustering to group structurally similar songs.

6. **Recommendation Logic**

   * Identify cluster membership
   * Rank songs within cluster using distance metrics
   * Return top-N similar songs

7. **Evaluation**

   * Silhouette score
   * Intra-cluster vs inter-cluster distance comparison
   * Cross-genre distribution analysis

---

## Dataset

Primary dataset options:

* [Spotify Songs with Attributes and Lyrics (Kaggle)](https://www.kaggle.com/datasets/bwandowando/spotify-songs-with-attributes-and-lyrics)

Required fields:

* Title
* Artist
* Lyrics

Optional (evaluation only):

* Genre

Audio features, popularity metrics, and external metadata are excluded from clustering.

---

## Project Structure

```
approot/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── src/
│   ├── preprocessing/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   └── utils/
│
├── notebooks/
├── configs/
├── reports/
│   ├── figures/
│   └── documentation/
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Technologies Used

* Python
* Pandas
* NumPy
* Scikit-learn

---

## Key Design Principles

* Unsupervised learning only
* No deep learning or transformer-based models
* No semantic embeddings
* Fully explainable feature-based similarity
* Modular and reproducible codebase

---

## Expected Outcome

Given an input song, the system:

1. Identifies its lyrical pattern cluster
2. Computes similarity within that cluster
3. Returns structurally similar songs across genres

The result is a genre-independent, interpretable lyric-based recommendation system.

---

## Academic Positioning

This project demonstrates the application of pattern recognition and unsupervised clustering to creative textual data. It provides an explainable alternative to black-box recommendation systems while maintaining computational efficiency and methodological transparency.

---

## License

This project is developed for academic purposes as part of a Minor Project submission.

---

## Recent changes

* **v0.0.5 — Feature Extraction Pipeline Initialization**

   * Added initial feature extraction module at `src/features/extract_features.py` that loads `data/processed/spotify_clean.csv`, validates required columns (`id`, `title`, `artist`, `lyrics`), removes rows with missing lyrics, and adds a helper `_word_count` column used for later feature extraction. Basic diagnostics (total, avg, min, max word counts) are printed on load.
