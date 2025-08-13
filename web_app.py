# web_app.py
import subprocess
import sys
import os
from flask import Flask, flash, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, abort
from database import (
    add_vk_user, load_vk_ids, delete_vk_user, load_user_visits_for_chart,
    load_archived_users, restore_user_from_archive, load_activity_stats,
    load_weekly_activity_stats, load_city_activity_stats
)
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, SECRET_KEY
from datetime import datetime
from config import OUTPUT_HTML

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/')
def index():
    vk_users = load_vk_ids()
    active_users = load_vk_ids()
    archived_users = load_archived_users(50)
    return render_template('index.html', users=active_users, archived_users=archived_users)

@app.route('/run-main-py', methods=['POST'])
def run_main_py():
    """Runs main.py as a subprocess and returns the result."""
    try:
        print("🔄 /run-main-py: Starting main.py...")
        # - Get the path to main.py relative to the current file -
        main_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')

        if not os.path.exists(main_script_path):
            error_msg = f"❌ /run-main-py: File main.py not found at path: {main_script_path}"
            print(error_msg)
            return jsonify({"status": "error", "message": error_msg}), 404

        # - Run main.py as a subprocess -
        # Using the same Python interpreter as for web_app.py
        result = subprocess.run(
            [sys.executable, main_script_path],
            capture_output=True,
            text=True,
            timeout=300  # Timeout 5 minutes (300 seconds)
        )

        if result.returncode == 0:
            success_msg = "✅ /run-main-py: main.py executed successfully!"
            print(success_msg)
            print(" → stdout:", result.stdout[-500:])  # Print last 500 characters of stdout
            return jsonify({"status": "success", "message": success_msg})
        else:
            error_msg = result.stderr[-1000:] if result.stderr else "Unknown error"
            print(f"❌ /run-main-py: Error executing main.py (code {result.returncode})")
            print(" → stderr:", error_msg)
            return jsonify({"status": "error", "message": f"main.py finished with error: {error_msg}"}), 500

    except subprocess.TimeoutExpired:
        error_msg = "⏳ /run-main-py: main.py is taking too long (> 5 minutes) and was terminated."
        print(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 408  # 408 Request Timeout

    except Exception as e:
        import traceback
        error_msg = f"❌ /run-main-py: Failed to run main.py: {e}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": error_msg}), 500

@app.route('/api/user_visits/<int:user_id>')
def api_get_user_visits(user_id):
    try:
        visits = load_user_visits_for_chart(user_id)
        return jsonify(visits)
    except Exception as e:
        print(f"❌ Error loading visit data for user_id={user_id}: {e}")
        return jsonify([]), 500  # Return empty array and 500 code in case of error

@app.route('/monitoring')
def monitoring_page():
    try:
        if not os.path.exists(OUTPUT_HTML):
            from main import generate_html_only  # Import the function
            generate_html_only()
        return send_from_directory(
            directory=os.path.dirname(os.path.abspath(OUTPUT_HTML)),
            path=os.path.basename(OUTPUT_HTML)
        )
    except Exception as e:
        print(f"❌ Error serving HTML page: {e}")
        abort(500)

@app.route('/statistics')
def statistics():
    """Page with user activity statistics."""
    try:
        print("📊 Loading data for statistics...")
        
        hourly_stats = load_activity_stats()      # <<< Load hourly statistics
        weekly_stats = load_weekly_activity_stats()  # <<< Load weekly activity statistics
        city_stats = load_city_activity_stats(20)   # <<< Load city statistics

        print(f"   → Hourly activity (first 3): {hourly_stats[:3] if hourly_stats else 'No data'}")
        print(f"   → Weekly activity (first 3): {weekly_stats[:3] if weekly_stats else 'No data'}")
        print(f"   → City activity (first 3): {city_stats[:3] if city_stats else 'No data'}")

        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        rendered_page = render_template(
            'statistics.html', 
            hourly_stats=hourly_stats,   # <<< Pass hourly statistics
            weekly_stats=weekly_stats,   # <<< Pass weekly statistics
            city_stats=city_stats,       # <<< Pass city statistics
            current_time=current_time
        )
        print("✅ Statistics page generated.")
        return rendered_page
    except Exception as e:
        import traceback
        print(f"❌ Error in /statistics route: {e}")
        print(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/restore/<int:archived_id>', methods=['POST'])
def restore_user(archived_id):
    success = restore_user_from_archive(archived_id)
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_user():
    vk_ids_str = request.form.get('vk_ids', '').strip()  # <<< Now 'vk_ids'
    if not vk_ids_str:
        flash("❌ Please enter user ID(s).", "error")
        return redirect(url_for('index'))

    vk_id_parts = [part.strip() for part in vk_ids_str.split(',')]
    added_ids = []
    invalid_ids = []
    duplicate_ids = []

    for part in vk_id_parts:
        if not part:
            continue  # Skip empty parts
        try:
            vk_id = int(part)
            if vk_id <= 0:
                raise ValueError("ID must be a positive number.")
            success = add_vk_user(vk_id)
            if success:
                added_ids.append(vk_id)
            else:
                duplicate_ids.append(vk_id)
        except ValueError:
            invalid_ids.append(part)

    if added_ids:
        flash(f"✅ User(s) with ID {', '.join(map(str, added_ids))} successfully added.", "success")
    if duplicate_ids:
        flash(f"ℹ️ User(s) with ID {', '.join(map(str, duplicate_ids))} already exist(s) in the list.", "info")
    if invalid_ids:
        flash(f"❌ The following values are not valid IDs: {', '.join(invalid_ids)}.", "error")
    
    return redirect(url_for('index'))

@app.route('/delete/<int:user_db_id>', methods=['POST'])
def delete_user(user_db_id):
    success = delete_vk_user(user_db_id)
    if success:
        flash(f"✅ User with ID {user_db_id} successfully deleted.", "success")
    else:
        flash(f"❌ Error deleting user with ID {user_db_id}.", "error")
    return redirect(url_for('index'))

@app.route('/run-monitoring')
def run_monitoring():
    try:
        main_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        result = subprocess.run(
            [sys.executable, main_script_path], 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        if result.returncode == 0:
            flash("✅ Monitoring completed successfully!", "success")
        else:
            error_msg = result.stderr[:500]  # Limit length for security
            flash(f"❌ Error during monitoring execution: {error_msg}", "error")
    except subprocess.TimeoutExpired:
        flash("⏳ Monitoring is taking too long and was terminated.", "error")
    except Exception as e:
        flash(f"❌ Failed to start monitoring: {e}", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("🚀 Starting Flask web interface for user management...")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
