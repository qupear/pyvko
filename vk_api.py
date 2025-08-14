# vk_api.py
import requests
import time
from datetime import datetime
from config import VK_ACCESS_TOKEN, API_VERSION
from database import save_to_db

def get_users_info(vk_id_pairs):
    Requests basic information and additional counters."""
    if not VK_ACCESS_TOKEN or VK_ACCESS_TOKEN.strip() == '' or VK_ACCESS_TOKEN == 'your_token_here':
        print("❌ Error: VK_ACCESS_TOKEN is not set in config.py")
        return []
    
    all_users = []
    chunk_size = 95
    
    for i in range(0, len(vk_id_pairs), chunk_size):
        chunk_pairs = vk_id_pairs[i:i + chunk_size]
        chunk_vk_ids = [str(pair[1]) for pair in chunk_pairs]
        user_ids_str = ','.join(chunk_vk_ids)
        
        print(f"🔍 Requesting basic data for {len(chunk_vk_ids)} users...")
        
        url = "https://api.vk.com/method/users.get"
        params = {
            'user_ids': user_ids_str,
            'fields': 'online,photo_200,last_seen,city,bdate,relation,counters,domain',
            'access_token': VK_ACCESS_TOKEN,
            'v': API_VERSION
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'error' in data:
                print(f"❌ VK API Error: {data['error']['error_msg']}")
                time.sleep(1)
                continue
            
            users = data['response']
            user_dict = {user['id']: user for user in users}
            
            for db_id, vk_id in chunk_pairs:
                if vk_id in user_dict:
                    vk_user = user_dict[vk_id]
                    
                    city = vk_user.get('city', {}).get('title') or None
                    bdate = vk_user.get('bdate')
                    relation = vk_user.get('relation')
                    
                    counters = vk_user.get('counters', {})
                    friends_count_from_counters = counters.get('friends')
                    photos_count = counters.get('photos')
                    # Note: followers and subscriptions often NOT included in counters
                    
                    friends_count = None
                    followers_count = None
                    subscriptions_count = None
                    groups_count = None
                    domain = vk_user.get('domain')
                    
                    print(f" 📊 Requesting additional counters for {vk_user.get('first_name', 'First Name')} {vk_user.get('last_name', 'Last Name')} (ID: {vk_id})...")
                    
                    try:
                        friends_resp = requests.get("https://api.vk.com/method/friends.get", params={
                            'user_id': vk_id,
                            'access_token': VK_ACCESS_TOKEN,
                            'v': API_VERSION,
                            'count': 0,
                            'offset': 0
                        }, timeout=5)
                        friends_data = friends_resp.json()
                        if 'response' in friends_data and 'count' in friends_data['response']:
                            friends_count = friends_data['response']['count']
                        elif 'error' in friends_data:
                            print(f" ⚠️ friends.get error: {friends_data['error']['error_msg']}")
                    except Exception as e:
                        print(f" ⚠️ friends.get exception: {e}")
                    
                    try:
                        followers_resp = requests.get("https://api.vk.com/method/users.getFollowers", params={
                            'user_id': vk_id,
                            'access_token': VK_ACCESS_TOKEN,
                            'v': API_VERSION,
                            'count': 0,
                            'offset': 0
                        }, timeout=5)
                        followers_data = followers_resp.json()
                        if 'response' in followers_data and 'count' in followers_data['response']:
                            followers_count = followers_data['response']['count']
                        elif 'error' in followers_data:
                            error_code = followers_data['error'].get('error_code', 0)
                            # Error codes: 15 - Access denied, 30 - Profile private/closed
                            if error_code in [15, 30]:
                                print(f" ℹ️ Followers access denied or profile closed for ID {vk_id} (Error {error_code})")
                            else:
                                print(f" ⚠️ users.getFollowers error: {followers_data['error']['error_msg']}")
                    except requests.exceptions.Timeout:
                        print(f" ⚠️ Timeout users.getFollowers for ID {vk_id}")
                    except Exception as e:
                        print(f" ⚠️ Exception users.getFollowers for ID {vk_id}: {e}")
                    
                    try:
                        subs_resp = requests.get("https://api.vk.com/method/users.getSubscriptions", params={
                            'user_id': vk_id,
                            'access_token': VK_ACCESS_TOKEN,
                            'v': API_VERSION,
                            'count': 0,
                            'extended': 0
                        }, timeout=5)
                        subs_data = subs_resp.json()
                        if 'response' in subs_data:
                            if 'users' in subs_data['response'] and 'count' in subs_data['response']['users']:
                                subscriptions_count = subs_data['response']['users']['count']
                            elif 'count' in subs_data['response']:
                                subscriptions_count = subs_data['response']['count']
                        elif 'error' in subs_data:
                            print(f" ⚠️ users.getSubscriptions error: {subs_data['error']['error_msg']}")
                    except Exception as e:
                        print(f" ⚠️ Exception users.getSubscriptions for ID {vk_id}: {e}")
                    
                    try:
                        groups_resp = requests.get("https://api.vk.com/method/groups.get", params={
                            'user_id': vk_id,
                            'access_token': VK_ACCESS_TOKEN,
                            'v': API_VERSION,
                            'count': 0,
                            'extended': 0
                        }, timeout=5)
                        groups_data = groups_resp.json()
                        if 'response' in groups_data and 'count' in groups_data['response']:
                            groups_count = groups_data['response']['count']
                        elif 'error' in groups_data:
                            error_code = groups_data['error'].get('error_code', 0)
                            if error_code == 15:
                                print(f" ℹ️ Group access denied for ID {vk_id} (Private)")
                            elif error_code == 30:
                                print(f" ℹ️ Profile ID {vk_id} is closed or blocked")
                            else:
                                print(f" ⚠️ groups.get error: {groups_data['error']['error_msg']}")
                    except requests.exceptions.Timeout:
                        print(f" ⚠️ Timeout groups.get for ID {vk_id}")
                    except Exception as e:
                        print(f" ⚠️ Exception groups.get for ID {vk_id}: {e}")
                    
                    wall_count = None
                    print(f" 🧱 Getting wall post count for {vk_user.get('first_name', 'First Name')} {vk_user.get('last_name', 'Last Name')} (ID: {vk_id})...")
                    try:
                        wall_resp = requests.get("https://api.vk.com/method/wall.get", params={
                            'owner_id': vk_id,
                            'count': 0,
                            'access_token': VK_ACCESS_TOKEN,
                            'v': API_VERSION
                        }, timeout=5)
                        wall_data = wall_resp.json()
                        if 'response' in wall_data:
                            wall_count = wall_data['response']['count']
                            print(f" ✅ Wall posts: {wall_count}")
                        elif 'error' in wall_data:
                            error_code = wall_data['error'].get('error_code', 0)
                            # Error codes: 15 - Access denied, 30 - Profile private/closed
                            if error_code in [15, 30]:
                                print(f" ℹ️ Wall is closed or inaccessible for ID {vk_id} (Error {error_code})")
                            else:
                                print(f" ⚠️ wall.get error: {wall_data['error']['error_msg']}")
                    except requests.exceptions.Timeout:
                        print(f" ⚠️ Timeout wall.get for ID {vk_id}")
                    except Exception as e:
                        print(f" ⚠️ Exception wall.get for ID {vk_id}: {e}")
                    
                    full_user = {
                        'id': vk_id,
                        'name': f"{vk_user.get('first_name', 'First Name')} {vk_user.get('last_name', 'Last Name')}",
                        'online': vk_user.get('online', 0),
                        'photo_200': vk_user.get('photo_200', 'https://vk.com/images/camera_200.png'),
                        'last_seen': vk_user.get('last_seen'),
                        'city': city,
                        'bdate': bdate,
                        'relation': relation,
                        'friends_count': friends_count,
                        'followers_count': followers_count,
                        'subscriptions_count': subscriptions_count,
                        'groups_count': groups_count,
                        'domain': domain,
                        'wall_count': wall_count,
                        'friends_count_from_counters': friends_count_from_counters,
                        'photos_count': photos_count
                    }
                    all_users.append(full_user)
                    
                    save_to_db(db_id, full_user)
                    
                    print(f" ✅ Processed: {full_user['name']} (Friends: {friends_count}, Followers: {followers_count})")
                    time.sleep(1)
                else:
                    print(f"⚠️ Failed to get basic data for VK ID: {vk_id}")
        
        except Exception as e:
            print(f"❌ Error in main API request: {e}")
        
        time.sleep(1)
    
    return all_users

def download_photo(url):
    """Downloads photo by URL.
    Returns binary data (bytes) or None in case of error."""
    try:
        print(f"📥 Downloading photo: {url}")
        response = requests.get(url, timeout=5)
        print(f"   → Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                print(f"   → Photo downloaded ({len(response.content)} bytes)")
                return response.content
            else:
                print(f"   ⚠️ URL is not an image: {content_type}")
                return None
        else:
            print(f"   ⚠️ Photo download error: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ⚠️ Photo download exception: {e}")
        return None

if __name__ == "__main__":
    print("This file is intended to import the get_users_info function.")
    # Example call:
    # users_data = get_users_info([(1, 1)])  # Pavel Durov
    # print(users_data)
