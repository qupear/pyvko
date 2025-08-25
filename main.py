# main.py
import argparse
import sys
import os
from config import VK_ACCESS_TOKEN, OUTPUT_HTML, APP_MODE
from database import load_vk_ids, load_users_with_latest_photos, load_city_activity_stats
from html_generator import generate_html, generate_birthday_calendar, generate_static_statistics_html
from utils import open_in_browser

def run_full_monitoring():
    print("🚀 Starting to check VKontakte users...\n")

    if not VK_ACCESS_TOKEN or VK_ACCESS_TOKEN.strip() == '' or VK_ACCESS_TOKEN == 'token':
        print("❌ Error: VK_ACCESS_TOKEN is not set in .env file")
        sys.exit(1)

    print("✅ Environment variables loaded.")
    print(f"🔧 Working mode: {APP_MODE.upper()}")

    vk_id_pairs = load_vk_ids()
    if not vk_id_pairs:
        print("❌ User list is empty.")
        sys.exit(1)

    print(f"✅ Loaded {len(vk_id_pairs)} users from DB.")

    from vk_api import get_users_info
    users_data_from_api = get_users_info(vk_id_pairs)

    if APP_MODE == 'memory':
        if not users_data_from_api:
            print("❌ No data for mode 'memory'.")
        else:
            print(f"\n🎨 Generate HTML for {len(users_data_from_api)} users (mode 'memory')...")
            generate_html(users_data_from_api)
            generate_birthday_calendar(users_data_from_api)

            print("\n🌐 open browser...")
            open_in_browser()

            print(f"\n✅ Ready! Done in mode 'memory'.")
        return

    latest_users = load_users_with_latest_photos()

    if not latest_users:
        print("❌ No data. Check data collection.")
    else:
        print(f"\n🎨 Generate HTML for {len(latest_users)} users...")
        generate_html(latest_users)
        generate_birthday_calendar(latest_users)

        print("\n🌐 open browser...")
        open_in_browser()

        print(f"\n✅ Ready! Check done.")

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
