#!/usr/bin/env python3
"""
Quick CLI tool to check scheduled posts.
"""
import json
from pathlib import Path
from datetime import datetime


def format_datetime(iso_string):
    """Format ISO datetime to readable format."""
    dt = datetime.fromisoformat(iso_string)
    return dt.strftime("%b %d, %Y at %I:%M %p")


def time_until(iso_string):
    """Calculate time until scheduled."""
    scheduled = datetime.fromisoformat(iso_string)
    now = datetime.now()
    diff = scheduled - now
    
    if diff.total_seconds() < 0:
        hours = abs(int(diff.total_seconds() / 3600))
        days = abs(int(hours / 24))
        if days > 0:
            return f"{days}d ago"
        return f"{hours}h ago"
    
    hours = int(diff.total_seconds() / 3600)
    days = int(hours / 24)
    
    if days > 0:
        return f"in {days}d"
    if hours > 0:
        return f"in {hours}h"
    return "very soon"


def print_table(data, headers):
    """Simple table printer without external dependencies."""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_row = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in data:
        print("  ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))


def main():
    # Find scheduled.json
    script_dir = Path(__file__).parent
    scheduled_file = script_dir / "output" / "scheduled.json"
    
    if not scheduled_file.exists():
        print("❌ No scheduled posts found.")
        print(f"   Looking for: {scheduled_file}")
        return
    
    # Load schedules
    with open(scheduled_file, 'r') as f:
        schedules = json.load(f)
    
    if not schedules:
        print("📭 No scheduled posts yet.")
        print("   Schedule posts from the web UI: http://localhost:8000")
        return
    
    # Print summary
    total = len(schedules)
    pending = sum(1 for s in schedules if s['status'] == 'scheduled')
    published = sum(1 for s in schedules if s['status'] == 'published')
    failed = sum(1 for s in schedules if s['status'] == 'failed')
    
    print("\n" + "="*80)
    print(f"  📅 SCHEDULED POSTS SUMMARY")
    print("="*80)
    print(f"  Total: {total} | Pending: {pending} | Published: {published} | Failed: {failed}")
    print("="*80 + "\n")
    
    # Sort by scheduled time (newest first)
    schedules.sort(key=lambda x: x['scheduled_time'], reverse=True)
    
    # Prepare table data
    table_data = []
    for schedule in schedules:
        status_icon = {
            'scheduled': '⏰',
            'published': '✅',
            'failed': '❌'
        }.get(schedule['status'], '❓')
        
        platforms = ', '.join(schedule.get('metadata', {}).get('platforms', []))
        
        table_data.append([
            schedule['reel_id'][:8],
            format_datetime(schedule['scheduled_time']),
            time_until(schedule['scheduled_time']),
            platforms,
            f"{status_icon} {schedule['status']}",
            schedule['caption'][:30] + '...' if len(schedule['caption']) > 30 else schedule['caption']
        ])
    
    # Print table
    headers = ['Reel ID', 'Scheduled For', 'Time', 'Platforms', 'Status', 'Caption']
    print_table(table_data, headers)
    
    print("\n" + "="*80)
    print(f"  💡 View full details: http://localhost:8000/scheduled")
    print("="*80 + "\n")
    
    # Show any failed posts with errors
    failed_posts = [s for s in schedules if s['status'] == 'failed']
    if failed_posts:
        print("\n⚠️  FAILED POSTS:\n")
        for post in failed_posts:
            print(f"  Reel {post['reel_id'][:8]}:")
            print(f"  Error: {post.get('publish_error', 'Unknown error')}\n")


if __name__ == "__main__":
    main()
