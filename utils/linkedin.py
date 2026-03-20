def get_linkedin_stats(post_url):
    """
    LinkedIn does NOT allow fetching likes/comments/shares via API
    for personal or company posts.

    This function exists to keep the workflow consistent
    and avoid backend crashes.
    """

    return {
        "likes": 0,
        "comments": 0,
        "shares": 0
    }
