# tests/test_database.py
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import connect_db, load_vk_ids, save_to_db, load_users_with_latest_photos

class TestDatabase(unittest.TestCase):

    def test_connect_db(self):
        """Tests database connection."""
        conn = connect_db()
        self.assertIsNotNone(conn, "❌ connect_db() returned None")
        if conn:
            conn.close()
        print("✅ test_connect_db: Database connection successful.")

    def test_load_vk_ids(self):
        """Tests loading the list of users."""
        ids = load_vk_ids()
        self.assertIsInstance(ids, list, "❌ load_vk_ids() should return a list")
        print(f"✅ test_load_vk_ids: Loaded {len(ids)} user IDs.")

    def test_save_and_load_user(self):
        """Tests saving and loading a test user."""
        # Create test data
        test_user_data = {
            'id': 1,  # VK ID
            'name': 'Test User',
            'online': 1,
            'photo_200': 'https://vk.com/images/camera_200.png  ',
            'last_seen': {'time': 1700000000},  # 14.11.2023 08:13:20 UTC
            'city': 'Moscow',
            'bdate': '01.01.1990',
            'relation': 1,
            'friends_count': 100,
            'followers_count': 50,
            'subscriptions_count': 20,
            'groups_count': 30,
            'domain': 'test_user'
        }

        user_id_db = 1  # vk_users.id table

        save_to_db(user_id_db, test_user_data)
        print("✅ test_save_and_load_user: Data saved.")

        users = load_users_with_latest_photos()
        self.assertIsInstance(users, list, "❌ load_users_with_latest_photos() should return a list")

        test_user_found = None
        for user in users:
            if user['user_id'] == user_id_db:
                test_user_found = user
                break

        self.assertIsNotNone(test_user_found, "❌ Test user not found after saving")
        self.assertEqual(test_user_found['name'], test_user_data['name'], "❌ User name does not match")
        self.assertEqual(test_user_found['online'], test_user_data['online'], "❌ Online status does not match")
        self.assertEqual(test_user_found['city'], test_user_data['city'], "❌ City does not match")
        self.assertEqual(test_user_found['bdate'], test_user_data['bdate'], "❌ Birth date does not match")
        self.assertEqual(test_user_found['relation'], test_user_data['relation'], "❌ Relationship status does not match")
        self.assertEqual(test_user_found['friends_count'], test_user_data['friends_count'],
                         "❌ Friends count does not match")
        self.assertEqual(test_user_found['followers_count'], test_user_data['followers_count'],
                         "❌ Followers count does not match")
        self.assertEqual(test_user_found['subscriptions_count'], test_user_data['subscriptions_count'],
                         "❌ Subscriptions count does not match")
        self.assertEqual(test_user_found['groups_count'], test_user_data['groups_count'],
                         "❌ Groups count does not match")
        self.assertEqual(test_user_found['domain'], test_user_data['domain'], "❌ Domain does not match")

        print("✅ test_save_and_load_user: Data loaded successfully and matches.")


if __name__ == '__main__':
    unittest.main()
