# Logo Similarity — Veridion Challenge

## Overview

This project solves the **Logo Similarity Challenge** from **Veridion**.  
The goal is to **extract, compare, and group logos** from a large set of company websites, identifying those that share the same or visually similar brand identity — without using any machine learning clustering algorithms (e.g. k-means, DBSCAN).

The solution focuses on **clarity, reproducibility, and interpretability** rather than complexity.

---

## Pipeline Overview

The pipeline consists of four main stages, each handled by a dedicated script:

| Stage | Script | Description |
|-------|---------|-------------|
| 1. Extraction | `download_logos.py` | Downloads company logos by analyzing website HTML metadata, favicon links, and image elements. |
| 2. Inspection | `inspect_logos.py` | Validates the downloaded files, ensuring they are readable image formats. |
| 3. Grouping | `group_logos.py` | Computes perceptual hashes (pHash) for each logo and groups them by visual similarity. |
| 4. Aggregation | `make_csv.py` | Combines all outputs into clean CSV files for reporting and analysis. |

---

## How It Works

### 1. Logo Extraction
- Each website URL is scanned for likely logo candidates using:
  - `<meta property="og:image">`
  - `<link rel="icon">`, `<link rel="apple-touch-icon">`
  - `<img>` tags containing “logo” or “brand” in the `alt` or `src` attributes.
- The first valid image is downloaded and stored in `logos_downloaded/`.

### 2️. Validation
`inspect_logos.py` checks that each file is a valid image (PNG, JPG, SVG, ICO, etc.) using Pillow (`PIL.Image.open`).  
Invalid or corrupted images are logged for review.

### 3️. Perceptual Hashing & Grouping
- Each image is converted to grayscale and resized to a standard resolution.
- The **pHash** algorithm generates a 64-bit fingerprint for visual structure.
- Logos with **Hamming distance ≤ 8** between hashes are grouped together.
- The result is a list of **groups of visually similar logos**.

### 4️. Data Output
All results are exported as CSVs:
- `logos_found.csv` — domains and logo URLs
- `logo_groups.csv` — final logo clusters and hash values

--- 

## Technical Details

- **Language:** Python 3.10+  
- **Key Libraries:**
  - `requests`, `beautifulsoup4` — HTML parsing and HTTP fetching  
  - `Pillow`, `imagehash` — image processing and perceptual hashing  
  - `pandas`, `pyarrow` — data handling and parquet reading  

- **Similarity Metric:** Hamming distance between 64-bit perceptual hashes.  
  ```
  if hash1 - hash2 <= 8:
      # logos considered similar
  ```

---
