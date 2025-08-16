# main.py
import argparse
import sys
import os
from config import VK_ACCESS_TOKEN, OUTPUT_HTML
from database import load_vk_ids, load_users_with_latest_photos, load_city_activity_stats
from html_generator import generate_html, generate_birthday_calendar, generate_static_statistics_html
from utils import open_in_browser

def run_full_monitoring():
    print("🚀 Starting to check VKontakte users...\n")

    if not VK_ACCESS_TOKEN or VK_ACCESS_TOKEN.strip() == '' or VK_ACCESS_TOKEN == 'your_token_here':
        print("❌ Error: VK_ACCESS_TOKEN is not set in .env file")
        sys.exit(1)

    print("✅ Environment variables loaded.")

    vk_id_pairs = load_vk_ids()
    if not vk_id_pairs:
        print("❌ User list is empty.")
        sys.exit(1)

    print(f"✅ Loaded {len(vk_id_pairs)} users from DB.")
    from database import load_activity_stats, load_weekly_activity_stats
    from html_generator import generate_static_statistics_html

    print("\n📊 Generating static statistics page...")
    hourly_stats = load_activity_stats()
    weekly_stats = load_weekly_activity_stats()
    city_stats = load_city_activity_stats(20)
    generate_static_statistics_html(hourly_stats, weekly_stats, city_stats)

    from vk_api import get_users_info  
    users_data_from_api = get_users_info(vk_id_pairs)

    latest_users = load_users_with_latest_photos()

    if not latest_users:
        print("❌ No data to display. Make sure the script successfully collected data.")
    else:
        print(f"\n🎨 Generating HTML page for {len(latest_users)} users...")
        generate_html(latest_users)
        generate_birthday_calendar(latest_users)  # Generate calendar

        print("\n🌐 Opening in browser...")
        open_in_browser()

        print(f"\n✅ Done! Check completed.")

def generate_html_only():
    """Generate HTML page only from the latest DB data."""
    print("📂 Generating HTML page from the latest DB data...\n")

    latest_users = load_users_with_latest_photos()

    if not latest_users:
        print("❌ No data to display in DB.")
        sys.exit(1)
    else:
        print(f"🎨 Generating HTML page for {len(latest_users)} users...")
        generate_html(latest_users)
        generate_birthday_calendar(latest_users)

        print("🌐 Opening in browser...")
        open_in_browser()

        print(f"\n✅ HTML page updated!")

def main():
    parser = argparse.ArgumentParser(
        description="VKontakte users monitoring",
        epilog="Examples:\n"
               "  python main.py
               "  python main.py --view    # HTML generation only from DB\n"
    )
    parser.add_argument(
        '--view', '-v',
        action='store_true',
        help='Generate HTML page from the latest DB data without connecting to VK API'
    )

    args = parser.parse_args()

    if args.view:
        generate_html_only()
    else:
        run_full_monitoring()

if __name__ == "__main__":
    main()
