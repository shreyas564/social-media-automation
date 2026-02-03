import requests

GRAPH_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"


def safe_get(url, params):
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print("FB API ERROR:", response.text)
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print("FB REQUEST FAILED:", e)
        return None


# ==========================
# FACEBOOK POST STATS
# ==========================

def get_facebook_likes_count(post_id, access_token):
    url = f"{BASE_URL}/{post_id}/reactions"
    params = {
        "summary": "true",
        "limit": 0,
        "access_token": access_token
    }

    data = safe_get(url, params)
    return data.get("summary", {}).get("total_count", 0) if data else 0


def get_facebook_comments_count(post_id, access_token):
    url = f"{BASE_URL}/{post_id}/comments"
    params = {
        "summary": "true",
        "limit": 0,
        "access_token": access_token
    }

    data = safe_get(url, params)
    return data.get("summary", {}).get("total_count", 0) if data else 0


def get_share_count(post_id, access_token):
    url = f"{BASE_URL}/{post_id}"
    params = {
        "fields": "shares",
        "access_token": access_token
    }

    data = safe_get(url, params)
    return data.get("shares", {}).get("count", 0) if data else 0


# ==========================
# INSTAGRAM BUSINESS ACCOUNT ID
# ==========================

def get_insta_user_id(token, page_id):
    url = f"{BASE_URL}/{page_id}"
    params = {
        "fields": "instagram_business_account",
        "access_token": token
    }

    data = safe_get(url, params)
    if not data:
        return None

    return data.get("instagram_business_account", {}).get("id")
