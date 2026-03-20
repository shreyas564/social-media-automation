# utils/instagram.py

def get_instagram_stats(post_url):
    """
    Instagram Graph API stats require Business account + permissions.
    For now, return safe defaults to keep workflow stable.
    """

    return {
        "likes": 0,
        "comments": 0,
        "shares": 0
    }
