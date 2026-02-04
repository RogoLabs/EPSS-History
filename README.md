# EPSS-History

Historical archive of EPSS (Exploit Prediction Scoring System) scores from [FIRST.org](https://www.first.org/epss/).

## About EPSS

The Exploit Prediction Scoring System (EPSS) is a data-driven effort for estimating the likelihood (probability) that a software vulnerability will be exploited in the wild. It produces a probability score between 0 and 1 (0% to 100%), where higher scores indicate greater probability of exploitation.

## Data Structure

EPSS CSV files are organized by Year and Month:

```
data/
├── 2021/
│   ├── 04/
│   │   ├── epss_scores-2021-04-14.csv.gz
│   │   └── ...
│   └── ...
├── 2024/
│   ├── 01/
│   │   ├── epss_scores-2024-01-01.csv.gz
│   │   └── ...
│   └── ...
└── 2025/
    └── ...
```

## Data Source

Files are downloaded from the EPSS API:
- URL format: `https://epss.empiricalsecurity.com/epss_scores-YYYY-MM-DD.csv.gz`
- Data available from: **April 14, 2021** onwards

## Automated Updates

This repository is automatically updated daily via GitHub Actions. The workflow runs at 1:30 PM UTC / 7:30 AM Central (after EPSS scores are published around 1:30 PM UTC).

### Manual Downloads

You can also trigger manual downloads via the GitHub Actions workflow:

1. Go to **Actions** → **Daily EPSS Download**
2. Click **Run workflow**
3. Options:
   - **Download all historical files**: Downloads all EPSS files from April 2021 to present
   - **Start date / End date**: Download a specific date range

## Local Usage

### Prerequisites

- Python 3.8+
- `requests` library

### Installation

```bash
pip install -r scripts/requirements.txt
```

### Download Commands

```bash
# Download today's file (daily update)
python scripts/download_epss.py --today

# Download all historical files
python scripts/download_epss.py --all

# Download files for a specific date range
python scripts/download_epss.py --start 2024-01-01 --end 2024-12-31

# Download a specific date
python scripts/download_epss.py --date 2024-06-15

# Decompress all downloaded .gz files
python scripts/download_epss.py --decompress

# Specify custom output directory
python scripts/download_epss.py --today --output-dir my_data
```

## CSV File Format

Each gzipped CSV file contains:

| Column | Description |
|--------|-------------|
| `cve` | CVE identifier (e.g., CVE-2021-44228) |
| `epss` | EPSS probability score (0-1) |
| `percentile` | Percentile ranking compared to all other CVEs |

## License

EPSS data is provided by FIRST.org. Please refer to their [terms of use](https://www.first.org/epss/) for data usage policies.
