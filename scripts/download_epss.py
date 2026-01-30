#!/usr/bin/env python3
"""
Download EPSS (Exploit Prediction Scoring System) CSV files.
Files are stored in Year/Month folder structure (e.g., 2025/01/).
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

BASE_URL = "https://epss.empiricalsecurity.com/epss_scores-{date}.csv.gz"
# EPSS data is available starting from 2021-04-14
EPSS_START_DATE = datetime(2021, 4, 14)


def get_output_path(date: datetime, base_dir: str = "data") -> Path:
    """Generate the output path for a given date in Year/Month format."""
    year = date.strftime("%Y")
    month = date.strftime("%m")
    filename = f"epss_scores-{date.strftime('%Y-%m-%d')}.csv.gz"
    return Path(base_dir) / year / month / filename


def download_epss_file(date: datetime, base_dir: str = "data", overwrite: bool = False) -> bool:
    """
    Download EPSS CSV file for a specific date.
    
    Args:
        date: The date to download EPSS scores for
        base_dir: Base directory for storing files
        overwrite: If True, download even if file exists
        
    Returns:
        True if file was downloaded successfully, False otherwise
    """
    output_path = get_output_path(date, base_dir)
    
    # Skip if file already exists and we're not overwriting
    if output_path.exists() and not overwrite:
        print(f"File already exists: {output_path}")
        return True
    
    url = BASE_URL.format(date=date.strftime("%Y-%m-%d"))
    
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            # Create directory structure
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Saved: {output_path}")
            return True
        elif response.status_code == 404:
            print(f"No data available for {date.strftime('%Y-%m-%d')}")
            return False
        else:
            print(f"Error downloading {url}: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False


def download_historical(start_date: datetime = None, end_date: datetime = None, 
                        base_dir: str = "data", overwrite: bool = False) -> dict:
    """
    Download historical EPSS files for a date range.
    
    Args:
        start_date: Start date (defaults to EPSS_START_DATE)
        end_date: End date (defaults to yesterday)
        base_dir: Base directory for storing files
        overwrite: If True, download even if files exist
        
    Returns:
        Dictionary with counts of successful and failed downloads
    """
    if start_date is None:
        start_date = EPSS_START_DATE
    
    if end_date is None:
        # EPSS scores are typically available for the previous day
        end_date = datetime.now() - timedelta(days=1)
    
    # Ensure we don't go before EPSS start date
    if start_date < EPSS_START_DATE:
        start_date = EPSS_START_DATE
    
    results = {"success": 0, "failed": 0, "skipped": 0}
    current_date = start_date
    
    while current_date <= end_date:
        output_path = get_output_path(current_date, base_dir)
        
        if output_path.exists() and not overwrite:
            results["skipped"] += 1
        elif download_epss_file(current_date, base_dir, overwrite):
            results["success"] += 1
        else:
            results["failed"] += 1
        
        current_date += timedelta(days=1)
    
    return results


def download_today(base_dir: str = "data") -> bool:
    """Download EPSS file for yesterday (most recent available)."""
    yesterday = datetime.now() - timedelta(days=1)
    return download_epss_file(yesterday, base_dir)


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download EPSS CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download yesterday's file (daily update)
  python download_epss.py --today
  
  # Download all historical files
  python download_epss.py --all
  
  # Download files for a specific date range
  python download_epss.py --start 2024-01-01 --end 2024-12-31
  
  # Download a specific date
  python download_epss.py --date 2024-06-15
        """
    )
    
    parser.add_argument("--today", action="store_true",
                        help="Download yesterday's EPSS file (most recent available)")
    parser.add_argument("--all", action="store_true",
                        help="Download all historical EPSS files")
    parser.add_argument("--date", type=str,
                        help="Download EPSS file for a specific date (YYYY-MM-DD)")
    parser.add_argument("--start", type=str,
                        help="Start date for range download (YYYY-MM-DD)")
    parser.add_argument("--end", type=str,
                        help="End date for range download (YYYY-MM-DD)")
    parser.add_argument("--output-dir", type=str, default="data",
                        help="Output directory (default: data)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing files")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.today, args.all, args.date, args.start]):
        parser.print_help()
        sys.exit(1)
    
    if args.today:
        success = download_today(args.output_dir)
        sys.exit(0 if success else 1)
    
    if args.date:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)
        success = download_epss_file(date, args.output_dir, args.overwrite)
        sys.exit(0 if success else 1)
    
    # Range download (--all or --start/--end)
    start_date = None
    end_date = None
    
    if args.start:
        try:
            start_date = datetime.strptime(args.start, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid start date format: {args.start}. Use YYYY-MM-DD")
            sys.exit(1)
    
    if args.end:
        try:
            end_date = datetime.strptime(args.end, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid end date format: {args.end}. Use YYYY-MM-DD")
            sys.exit(1)
    
    results = download_historical(start_date, end_date, args.output_dir, args.overwrite)
    
    print(f"\nDownload complete:")
    print(f"  Successful: {results['success']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Skipped (existing): {results['skipped']}")
    
    # Only exit with error if failure rate is significant (>5% of attempted downloads)
    # Some gaps in EPSS data are expected (weekends, holidays, maintenance)
    total_attempted = results['success'] + results['failed']
    if total_attempted > 0:
        failure_rate = results['failed'] / total_attempted
        # Exit successfully if we got most files (>95% success rate)
        # or if we have fewer than 10 failures (acceptable for historical gaps)
        if failure_rate <= 0.05 or results['failed'] <= 10:
            print(f"  Note: {results['failed']} missing files is within expected range (data gaps)")
            sys.exit(0)
        else:
            print(f"  Warning: High failure rate ({failure_rate:.1%})")
            sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
