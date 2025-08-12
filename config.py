# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')
API_VERSION = os.getenv('API_VERSION', '5.199')
OUTPUT_HTML = os.getenv('OUTPUT_HTML', 'vk_users_status.html')

CALENDAR_HTML = 'vk_birthday_calendar.html'

FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-key')
STATISTICS_HTML = os.getenv('STATISTICS_HTML', 'statistics.html')
