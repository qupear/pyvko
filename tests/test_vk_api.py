# tests/test_vk_api.py
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vk_api import get_users_info

class TestVkApi(unittest.TestCase):

    def test_get_users_info_structure(self):
        vk_id_pairs = [(1, 1)] # (db_id, vk_id)

        users_data = get_users_info(vk_id_pairs)

        self.assertIsInstance(users_data, list, "❌ get_users_info() should return a list")
        if not users_data:
            self.skipTest("⚠️ get_users_info() returned an empty list. Possibly no token or network is unavailable.")

        user = users_data[0]
        self.assertIn('id', user, "❌ Key 'id' is missing in user data")
        self.assertIn('name', user, "❌ Key 'name' is missing in user data")
        self.assertIn('online', user, "❌ Key 'online' is missing in user data")
        self.assertIn('photo_200', user, "❌ Key 'photo_200' is missing in user data")
        self.assertIn('last_seen', user, "❌ Key 'last_seen' is missing in user data")
        self.assertIn('city', user, "❌ Key 'city' is missing in user data")
        self.assertIn('bdate', user, "❌ Key 'bdate' is missing in user data")
        self.assertIn('relation', user, "❌ Key 'relation' is missing in user data")
        self.assertIn('friends_count', user, "❌ Key 'friends_count' is missing in user data")
        self.assertIn('followers_count', user, "❌ Key 'followers_count' is missing in user data")
        self.assertIn('subscriptions_count', user, "❌ Key 'subscriptions_count' is missing in user data")
        self.assertIn('groups_count', user, "❌ Key 'groups_count' is missing in user data")
        self.assertIn('domain', user, "❌ Key 'domain' is missing in user data")

        print(f"✅ test_get_users_info_structure: Data structure is correct for user {user['name']}.")

    def test_get_users_info_values(self):
        vk_id_pairs = [(1, 1)]
        users_data = get_users_info(vk_id_pairs)

        if not users_data:
            self.skipTest("⚠️ get_users_info() returned an empty list. Possibly no token or network is unavailable.")

        user = users_data[0]
        self.assertIsInstance(user['id'], int, "❌ 'id' should be an integer")
        self.assertGreater(user['id'], 0, "❌ 'id' should be positive")
        self.assertIsInstance(user['name'], str, "❌ 'name' should be a string")
        self.assertIn(user['online'], [0, 1], "❌ 'online' should be 0 or 1")
        self.assertIsInstance(user['photo_200'], str, "❌ 'photo_200' should be a string (URL)")
        self.assertTrue(user['photo_200'].startswith('http'), "❌ 'photo_200' should be a URL")
        if user['last_seen'] is not None:
            self.assertIsInstance(user['last_seen'], dict, "❌ 'last_seen' should be a dictionary or None")
            if 'time' in user['last_seen']:
                self.assertIsInstance(user['last_seen']['time'], int, "❌ 'last_seen.time' should be an integer")
        if user['friends_count'] is not None:
            self.assertIsInstance(user['friends_count'], int, "❌ 'friends_count' should be an integer or None")
        print(f"✅ test_get_users_info_values: Data values are correct for user {user['name']}.")

if __name__ == '__main__':
    unittest.main()
