# tests/test_html_generator.py
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from html_generator import generate_html, format_bdate, calculate_age

class TestHtmlGenerator(unittest.TestCase):

    def test_generate_html_no_error(self):
        """Checks that generate_html does not cause errors."""
        test_users_data = [
            {
                'user_id': 1,
                'name': 'Test User',
                'online': 1,
                'last_seen': 1700000000,
                'photo_base64': None,
                'city': 'Moscow',
                'bdate': '01.01.1990',
                'relation': 1,
                'friends_count': 100,
                'followers_count': 50,
                'subscriptions_count': 20,
                'groups_count': 30,
                'domain': 'test_user'
            }
        ]

        try:
            generate_html(test_users_data)
            html_generated = True
        except Exception as e:
            html_generated = False
            print(f"❌ Error in generate_html: {e}")

        self.assertTrue(html_generated, "❌ generate_html raised an exception")
        print("✅ test_generate_html_no_error: HTML generated without errors.")

    def test_format_bdate_full(self):
        bdate = "01.01.1990"
        expected = "1 January 1990"
        result = format_bdate(bdate)
        self.assertEqual(result, expected, f"❌ format_bdate('{bdate}') = '{result}', expected '{expected}'")
        print(f"✅ test_format_bdate_full: '{bdate}' -> '{result}'")

    def test_format_bdate_partial(self):
        bdate = "01.01"
        expected = "1 January"
        result = format_bdate(bdate)
        self.assertEqual(result, expected, f"❌ format_bdate('{bdate}') = '{result}', expected '{expected}'")
        print(f"✅ test_format_bdate_partial: '{bdate}' -> '{result}'")

    def test_calculate_age(self):
        from datetime import datetime
        current_year = datetime.now().year
        bdate = f"01.01.{current_year - 25}"
        expected = " (25)"
        result = calculate_age(bdate)
        self.assertEqual(result, expected, f"❌ calculate_age('{bdate}') = '{result}', expected '{expected}'")
        print(f"✅ test_calculate_age: '{bdate}' -> '{result}'")

if __name__ == '__main__':
    unittest.main()
