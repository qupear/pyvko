# html_generator.py
import os
from datetime import datetime
from config import OUTPUT_HTML

# --- Months in words ---
MONTHS = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

# --- Function: check if birthday is within 7 days ---
def is_birthday_soon(bdate):
    if not bdate or '.' not in bdate:
        return False
    parts = bdate.split('.')
    if len(parts) < 2:
        return False
    try:
        day, month = int(parts[0]), int(parts[1])
        today = datetime.now()
        current_year = today.year
        try:
            birthday_this_year = datetime(current_year, month, day)
        except ValueError:
            return False

        if birthday_this_year < today:
            birthday_this_year = datetime(current_year + 1, month, day)

        delta = (birthday_this_year - today).days
        return 0 <= delta <= 7
    except:
        return False

# --- Format birth date ---
def format_bdate(bdate):
    if not bdate or bdate == '—':
        return '—'
    parts = bdate.split('.')
    if len(parts) == 3:
        try:
            day, month, year = map(int, parts)
            return f"{day} {MONTHS[month]} {year}"
        except:
            return bdate
    elif len(parts) == 2:
        try:
            day, month = map(int, parts)
            return f"{day} {MONTHS[month]}"
        except:
            return bdate
    return bdate

# --- Age ---
def calculate_age(bdate):
    if not bdate or len(bdate.split('.')) != 3:
        return ''
    try:
        day, month, year = map(int, bdate.split('.'))
        today = datetime.now()
        age = today.year - year
        if (today.month, today.day) < (month, day):
            age -= 1
        return f" ({age})"
    except:
        return ''

# --- Relationship status ---
RELATION_MAP = {
    1: "single", 2: "in a relationship", 3: "engaged",
    4: "married", 5: "it's complicated", 6: "actively searching",
    7: "in love", 8: "in a civil union", 9: "not specified"
}

# --- Generate HTML ---
def generate_html(users_data):
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    # --- Collect statistics ---
    total = len(users_data)
    online_count = sum(1 for u in users_data if u['online'])
    hidden_count = sum(1 for u in users_data if not u.get('last_seen'))
    offline_count = total - online_count
    birthday_count = sum(1 for u in users_data if is_birthday_soon(u['bdate']))

    # --- Placeholder (base64) ---
    PLACEHOLDER = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VK Monitoring</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Include Chart.js from CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Include moment adapter for Chart.js (for time axis) -->
    <script src="https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.1/dist/chartjs-adapter-moment.min.js"></script>
    <!-- Include our external CSS file -->
    <link rel="stylesheet" href="static/css/styles.css">
    <!-- Include our external JS file -->
    <script defer src="static/js/main.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <button id="refreshBtn" class="refresh-btn" title="Run main.py to update data">🔄 Refresh Data</button>
            <a href="vk_birthday_calendar.html" target="_blank" class="header-link calendar-link">📅 Birthday Calendar</a>
            <a href="statistics.html" class="header-link stats-link">📊 Statistics</a>
            <h1>VK Monitoring</h1>
            <div class="time">Time: {current_time}</div>
            <div class="stats">
                Total: <span>{total}</span>
                Online: <span>{online_count}</span>
                Offline: <span>{offline_count}</span>
                Hidden: <span>{hidden_count}</span>
            </div>
        </header>

        <div class="filters">
            <button onclick="filter('all')" class="active">All</button>
            <button onclick="filter('online')">Online</button>
            <button onclick="filter('offline')">Offline</button>
            <button onclick="filter('hidden')">Hidden Time</button>
            <button onclick="filter('birthday')">Birthday within 7 days <span>({birthday_count})</span></button>
        </div>

        <div class="sort-controls">
            <button onclick="sort('name')">Name</button>
            <button onclick="sort('city')">City</button>
            <button onclick="sort('bdate')">Birthday</button>
            <button onclick="sort('last_seen')" class="active">Online</button>
        </div>

        <div class="users" id="users-container">
"""

    for user in users_data:
        if not user:
            continue
        status_class = 'online' if user['online'] else 'offline'
        status_text = 'Online' if user['online'] else 'Offline'

        last_seen_text = 'hidden'
        if user['last_seen']:
            dt = datetime.fromtimestamp(user['last_seen'])
            last_seen_text = dt.strftime('%d.%m %H:%M')

        data_filter = 'online' if user['online'] else 'offline'
        if not user['last_seen']:
            data_filter += ' hidden'
        if is_birthday_soon(user['bdate']):
            data_filter += ' birthday'

        # --- Generate photo ---
        src = PLACEHOLDER
        if user['photo_base64']:
            src = f"image/jpeg;base64,{user['photo_base64']}"

        card_class = 'user-card'
        if is_birthday_soon(user['bdate']):
            card_class += ' birthday-soon'

        formatted_bdate = format_bdate(user['bdate'])
        age_suffix = calculate_age(user['bdate']) if len(user['bdate'].split('.')) == 3 else ''
        relation_text = RELATION_MAP.get(user['relation'], '—')

        # --- Formatting domain line ---
        domain_line = ""
        if user.get('domain') and user['domain'] != 'id' + str(user['user_id']):
            # Form link that opens in new tab
            domain_url = f"https://vk.com/{user['domain']}"
            domain_line = f'<div class="domain-line"><a href="{domain_url}" target="_blank" class="dim">@{user["domain"]}</a></div>'

        # --- Formatting new counter fields ---
        counts_line_1 = ""
        counts_line_2 = ""
        
        # First line: Friends and Followers
        friends_part = f"Fr:{user['friends_count']}" if user.get('friends_count') is not None else ""
        followers_part = f"Fol:{user['followers_count']}" if user.get('followers_count') is not None else ""
        if friends_part or followers_part:
             counts_line_1 = f"<div>{friends_part}</div><div>{followers_part}</div>"
        
        # Second line: Subscriptions and Groups
        subs_part = f"Sub:{user['subscriptions_count']}" if user.get('subscriptions_count') is not None else ""
        groups_part = f"Gr:{user['groups_count']}" if user.get('groups_count') is not None else ""
        if subs_part or groups_part:
             counts_line_2 = f"<div>{subs_part}</div><div>{groups_part}</div>"

        html += f"""
        <div class="{card_class}" 
             data-filter="{data_filter}"
             data-name="{user['name'].lower()}"
             data-city="{user['city'].lower()}"
             data-bdate="{user['bdate'] or '9999'}"
             data-last-seen="{user['last_seen'] or 0}">
            <img class="user-photo" src="{src}" alt="Photo" onerror="this.src='{PLACEHOLDER}'; this.onerror=null;">
            <div class="user-name" title="{user['name']}">{user['name']}</div>
            <div class="status {status_class}">{status_text}</div>
            <div class="user-info">
                <div>{user['city']}</div>
                <div>{formatted_bdate}{age_suffix}</div>
                <div class="dim">{relation_text}</div>
                <div>{last_seen_text}</div>
                <!-- Domain line -->
                {domain_line}
                <!-- New counter lines -->
                <div class="counts-line">{counts_line_1}</div>
                <div class="counts-line">{counts_line_2}</div>
            </div>
        </div>
        """

    html += """
        </div>
    </div>

    <!-- Context menu -->
    <div id="contextMenu" class="context-menu">
        <ul>
            <li id="showChartBtn">Show Chart</li>
            <!-- Can add other items -->
        </ul>
    </div>

    <!-- Modal window for chart -->
    <div id="chartModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title" id="modalTitle">Visit Chart</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="chart-container">
                    <canvas id="visitChart"></canvas>
                </div>
            </div>
            <footer>
                <p>Data loaded from <code>user_status</code> table. Online: green, Offline: red.</p>
            </footer>
        </div>
    </div>

    <!-- Scroll buttons -->
    <div class="scroll-buttons">
        <button id="scrollToTopBtn" class="scroll-btn top-btn" title="Scroll to Top">&#8593;</button>
        <button id="scrollToBottomBtn" class="scroll-btn bottom-btn" title="Scroll to Bottom">&#8595;</button>
    </div>

</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"📄 HTML page saved: {os.path.abspath(OUTPUT_HTML)}")

# --- Generate statistics HTML ---
def generate_static_statistics_html(hourly_stats_data, weekly_stats_data, city_stats_data):
    """Generates HTML statistics page and saves it as a file."""
    from config import STATISTICS_HTML # Make sure STATISTICS_HTML is defined in config.py
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>User Activity Statistics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Include Chart.js and adapters from CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.1/dist/chartjs-adapter-moment.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f4f6f8;
            padding: 0;
            margin: 0;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        header {{
            background: #4c75a3;
            color: white;
            padding: 16px;
            text-align: center;
        }}
        header h1 {{
            margin: 0;
            font-size: 20px;
        }}
        .time {{
            font-size: 13px;
            opacity: 0.9;
        }}
        .back-link {{
            display: block;
            text-align: center;
            margin: 15px 0;
            color: #4c75a3;
            text-decoration: none;
            font-size: 14px;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 30px;
            padding: 20px;
        }}
        .chart-container {{
            width: 100%;
            height: 500px; /* Fixed height for chart */
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        @media (min-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
        @media (min-width: 1200px) {{
            .charts-grid {{
                grid-template-columns: 1fr 1fr 1fr; /* Three columns on wide screens */
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>User Activity Statistics</h1>
            <div class="time">Generation Time: {current_time}</div>
        </header>
        <a href="vk_users_status.html" class="back-link">← Back to User List</a>
        
        <div class="charts-grid">
            <!-- --- Chart 1: Activity by Hour of Day --->
            <div class="chart-wrapper">
                <h2 style="text-align: center;">Activity by Hour of Day</h2>
                <div class="chart-container">
                    <canvas id="hourlyActivityChart"></canvas>
                </div>
            </div>
            
            <!-- --- Chart 2: Activity by Day of Week --->
            <div class="chart-wrapper">
                <h2 style="text-align: center;">Activity by Day of Week</h2>
                <div class="chart-container">
                    <canvas id="weeklyActivityChart"></canvas>
                </div>
            </div>

            <!-- --- Chart 3: Activity by City (Top 20) --->
            <div class="chart-wrapper">
                <h2 style="text-align: center;">Activity by City (Top 20)</h2>
                <div class="chart-container">
                    <canvas id="cityActivityChart"></canvas>
                </div>
            </div>
            <!-- ------------------------------------------ -->
        </div>
        
        <footer>
            <p>Charts show the number of unique users who accessed the system at each hour/day/city according to Moscow time.</p>
        </footer>
    </div>

    <!-- --- Pass data from Python to JS via global variables --->
    <script>
        // These variables will be available in main.js
        window.STATS_DATA = {{
            hourly: {hourly_stats_data},
            weekly: {weekly_stats_data},
            city: {city_stats_data}
        }};
        console.log("📊 Statistics data loaded into window.STATS_DATA:", window.STATS_DATA);
    </script>
    <!-- ------------------------------------------------------------ -->

    <!-- Include our external JS file AFTER defining window.STATS_DATA -->
    <script defer src="static/js/main.js"></script>
</body>
</html>
"""

    with open(STATISTICS_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"📊 Static statistics page saved: {os.path.abspath(STATISTICS_HTML)}")

# --- Generate calendar (moved from main.py) ---
def generate_birthday_calendar(users_data):
    from config import CALENDAR_HTML
    calendar_filename = CALENDAR_HTML
    current_year = datetime.now().year
    birthdays_by_date = {}

    for user in users_data:
        bdate_str = user.get('bdate')
        if not bdate_str:
            continue
        parts = bdate_str.split('.')
        if len(parts) >= 2:
            try:
                day = int(parts[0])
                month = int(parts[1])
                _ = datetime(year=current_year, month=month, day=day)

                if (day, month) not in birthdays_by_date:
                    birthdays_by_date[(day, month)] = []
                user_info = {
                    'name': user['name'],
                    'year': int(parts[2]) if len(parts) == 3 else None
                }
                birthdays_by_date[(day, month)].append(user_info)
            except (ValueError, IndexError):
                continue

    MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    calendar_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Birthday Calendar</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f4f6f8;
            padding: 20px;
            margin: 0;
        }}
        .calendar-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        header {{
            background: #4c75a3;
            color: white;
            padding: 16px;
            text-align: center;
        }}
        header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .calendar-year {{
            text-align: center;
            font-size: 20px;
            margin: 10px 0;
        }}
        .months-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }}
        .month {{
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .month-header {{
            background-color: #eee;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
        }}
        .weekdays {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            background-color: #f9f9f9;
            font-weight: bold;
            font-size: 12px;
        }}
        .weekdays div {{
            padding: 5px;
            text-align: center;
            border-right: 1px solid #eee;
        }}
        .weekdays div:last-child {{
            border-right: none;
        }}
        .days {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
        }}
        .day {{
            border-right: 1px solid #eee;
            border-bottom: 1px solid #eee;
            min-height: 40px;
            padding: 2px;
            font-size: 12px;
            position: relative;
        }}
        .day:nth-child(7n) {{
             border-right: none;
        }}
        .day-number {{
            font-weight: bold;
            text-align: right;
            padding: 2px;
        }}
        .birthdays {{
            margin-top: 15px;
        }}
        .birthday-entry {{
            margin-bottom: 3px;
            padding: 2px;
            background-color: #e3f2fd;
            border-radius: 3px;
        }}
        .birthday-age {{
            font-size: 10px;
            color: #666;
        }}
        .empty-day {{
            background-color: #fafafa;
        }}
        .prev-month, .next-month {{
            color: #aaa;
        }}
    </style>
</head>
<body>
    <div class="calendar-container">
        <header>
            <h1>Birthday Calendar</h1>
        </header>
        <div class="calendar-year">{current_year}</div>
        <div class="months-grid">
"""

    for month_index in range(1, 13):
        month_name = MONTH_NAMES[month_index - 1]

        first_day_of_month = datetime(current_year, month_index, 1)
        start_day_offset = first_day_of_month.weekday()

        if month_index == 12:
            next_month = first_day_of_month.replace(year=current_year+1, month=1, day=1)
        else:
            next_month = first_day_of_month.replace(month=month_index+1, day=1)
        days_in_month = (next_month - first_day_of_month).days

        calendar_html += f"""            <div class="month">
                <div class="month-header">{month_name} {current_year}</div>
                <div class="weekdays">
"""
        for wd_name in WEEKDAY_NAMES:
             calendar_html += f"                    <div>{wd_name}</div>\n"
        calendar_html += "                </div>\n                <div class=\"days\">\n"

        prev_month_index = month_index - 1 if month_index > 1 else 12
        prev_year_for_prev_month = current_year if month_index > 1 else current_year - 1
        if prev_month_index == 12:
            prev_next_month = datetime(prev_year_for_prev_month + 1, 1, 1)
        else:
            prev_next_month = datetime(prev_year_for_prev_month, prev_month_index + 1, 1)
        prev_first_day = datetime(prev_year_for_prev_month, prev_month_index, 1)
        days_in_prev_month = (prev_next_month - prev_first_day).days

        for i in range(start_day_offset):
            day_num = days_in_prev_month - start_day_offset + i + 1
            calendar_html += f"                    <div class=\"day empty-day prev-month\"><div class=\"day-number\">{day_num}</div></div>\n"

        for day in range(1, days_in_month + 1):
            birthdays_today = birthdays_by_date.get((day, month_index), [])
            birthday_content = ""
            if birthdays_today:
                birthday_content = "<div class=\"birthdays\">"
                for person in birthdays_today:
                    name = person['name']
                    year = person['year']
                    age_part = ""
                    if year is not None:
                        try:
                            age = current_year - year
                            # Clarify if birthday has already passed this year
                            if (month_index, day) > (datetime.now().month, datetime.now().day):
                                age -= 1
                            age_part = f"<span class=\"birthday-age\">({age} y.o.)</span>"
                        except:
                            pass
                    birthday_content += f"<div class=\"birthday-entry\">{name} {age_part}</div>"
                birthday_content += "</div>"

            calendar_html += f"                    <div class=\"day\"><div class=\"day-number\">{day}</div>{birthday_content}</div>\n"

        total_cells_filled = start_day_offset + days_in_month
        next_month_days_needed = (7 - (total_cells_filled % 7)) % 7
        for i in range(next_month_days_needed):
            day_num = i + 1
            calendar_html += f"                    <div class=\"day empty-day next-month\"><div class=\"day-number\">{day_num}</div></div>\n"

        calendar_html += "                </div>\n            </div>\n"

    calendar_html += """        </div>
    </div>
</body>
</html>"""

    try:
        with open(calendar_filename, 'w', encoding='utf-8') as f:
            f.write(calendar_html)
        print(f"📅 Birthday calendar saved: {os.path.abspath(calendar_filename)}")
    except Exception as e:
        print(f"❌ Error saving calendar: {e}")
