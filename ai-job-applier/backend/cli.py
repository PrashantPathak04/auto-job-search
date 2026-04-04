#!/usr/bin/env python3
"""
Command Line Interface for AI Job Applier

Usage:
    python cli.py --keywords "Python Developer" --location "San Francisco" --max 5
    python cli.py --scrape-only --keywords "Data Scientist"
    python cli.py --status
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from job_application_pipeline import JobApplicationPipeline
from tracker.db_manager import get_db, get_applications


def main():
    parser = argparse.ArgumentParser(description="AI Job Applier CLI")
    parser.add_argument("--keywords", type=str, help="Job search keywords")
    parser.add_argument("--location", type=str, default="", help="Job location")
    parser.add_argument("--max", type=int, default=5, help="Maximum applications")
    parser.add_argument("--scrape-only", action="store_true", help="Only scrape, don't apply")
    parser.add_argument("--status", action="store_true", help="Show application status")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if not args.keywords:
        print("❌ Error: --keywords is required")
        parser.print_help()
        return

    # Run the pipeline
    pipeline = JobApplicationPipeline()

    try:
        if args.scrape_only:
            print("🔍 Scraping jobs only...")
            # Would implement scrape-only mode
            print("Scrape-only mode not yet implemented")
        else:
            print("🚀 Starting full application pipeline...")
            asyncio.run(pipeline.run_pipeline(
                keywords=args.keywords,
                location=args.location,
                max_applications=args.max
            ))
    finally:
        pipeline.cleanup()


def show_status():
    """Show current application status"""
    print("📊 Application Status")
    print("=" * 50)

    db = next(get_db())
    applications = get_applications(db)

    if not applications:
        print("No applications found.")
        return

    status_counts = {}
    for app in applications:
        status = app.status
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f"Total Applications: {len(applications)}")
    print()

    for status, count in status_counts.items():
        print(f"{status.title()}: {count}")

    print()
    print("Recent Applications:")
    print("-" * 30)

    # Show last 5 applications
    for app in applications[-5:]:
        print(f"• {app.job_title} at {app.company} - {app.status} ({app.applied_at.strftime('%Y-%m-%d')})")


if __name__ == "__main__":
    main()