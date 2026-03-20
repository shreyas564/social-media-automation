import logging
logger = logging.getLogger(__name__)

"""
Platform-Specific Apify Scrapers

This module contains scraper classes for each social media platform
using the proper Apify actors for likes and comments.
"""

import os
from typing import List, Dict, Tuple
from apify_client import ApifyClient
from datetime import datetime


class FacebookScraper:
    """Facebook-specific scrapers using proper Apify actors"""
    
    def __init__(self, apify_client: ApifyClient):
        self.client = apify_client
    
    def scrape_comments(self, post_url: str, max_comments: int = 100) -> List[str]:
        """
        Scrape commenters from Facebook post
        
        Actor: thedoor/facebook-comment-scraper
        """
        logger.info(f"🔍 [Facebook] Scraping comments from: {post_url}")
        
        run_input = {
            "postUrls": [post_url],
            "maxComments": max_comments,
            "commentsMode": "RANKED_THREADED"
        }
        
        try:
            # Run Facebook Comments Scraper
            # User requested 'thedoor/facebook-comment-scraper'
            logger.info(f"🔍 [Facebook] Using 'thedoor/facebook-comment-scraper' for: {post_url}")
            run = self.client.actor("thedoor/facebook-comment-scraper").call(run_input=run_input)
            
            commenters = []
            if run:
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    # Check multiple fields as different scrapers use different schemas
                    author_name = (
                        item.get('author_name') or  # 'thedoor' uses snake_case
                        item.get('name') or 
                        item.get('userName') or 
                        item.get('authorName') or 
                        item.get('author') or
                        item.get('profileName')
                    )
                    
                    # 'thedoor' sometimes hides author in 'user' object
                    if not author_name and item.get('user'):
                         author_name = item.get('user', {}).get('name') or item.get('user', {}).get('username')

                    if author_name:
                        commenters.append(author_name)
            
            logger.info(f"✓ Found {len(commenters)} commenters")
            return commenters
        
        except Exception as e:
            logger.info(f"❌ Error scraping Facebook comments: {e}")
            return []
    
    def scrape_likes(self, post_url: str, max_likes: int = 100) -> List[str]:
        """
        Scrape likers from Facebook post
        
        Actor: apify/facebook-likes-scraper
        
        Args:
            post_url: Facebook post URL
            max_likes: Maximum number of likes to fetch
        
        Returns:
            List of liker names
        """
        logger.info(f"🔍 [Facebook] Scraping likes from: {post_url}")
        
        # Correct input format for facebook-likes-scraper
        # Based on inspection, it likely expects startUrls with objects
        run_input = {
            "startUrls": [{"url": post_url}],
            "maxLikes": max_likes
        }
        
        try:
            # Run Facebook Likes Scraper
            run = self.client.actor("apify/facebook-likes-scraper").call(run_input=run_input)
            
            likers = []
            if run:
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    user_name = item.get('userName') or item.get('name') or item.get('profileName')
                    if user_name:
                        likers.append(user_name)
            
            logger.info(f"✓ Found {len(likers)} likers")
            return likers
        
        except Exception as e:
            logger.info(f"❌ Error scraping Facebook likes: {e}")
            return []


class InstagramScraper:
    """Instagram-specific scrapers using proper Apify actors"""
    
    def __init__(self, apify_client: ApifyClient, session_cookie: str = None):
        self.client = apify_client
        self.session_cookie = session_cookie  # Required for full liker list
    
    def scrape_comments(self, post_url: str, max_comments: int = 100) -> List[str]:
        """
        Scrape commenters from Instagram post
        
        Actor: datadoping/instagram-comments-and-replies-scraper
        """
        logger.info(f"🔍 [Instagram] Scraping comments from: {post_url}")
        
        run_input = {
            "code_or_id_or_url": [post_url],
            "resultsLimit": max_comments
        }
        
        # Add cookie if available
        if self.session_cookie:
            run_input["cookies"] = [{"name": "sessionid", "value": self.session_cookie, "domain": ".instagram.com", "path": "/"}]
        
        try:
            # Run Instagram Comments Scraper
            run = self.client.actor("datadoping/instagram-comments-and-replies-scraper").call(run_input=run_input)
            
            commenters = []
            if run:
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    # Check connection to filter out caption
                    # "content_type": "caption" or "type": "caption" based on screenshot
                    # The screenshot shows "Type" column with value "caption" or "comment"
                    # It also shows variable naming like "username", "user_id".
                    
                    item_type = item.get('type') or item.get('content_type')
                    if item_type == 'caption':
                        continue
                        
                    username = item.get('username') or item.get('ownerUsername')
                    if username:
                        commenters.append(username)
                        
            logger.info(f"✓ Found {len(commenters)} commenters")
            return commenters
        
        except Exception as e:
            logger.info(f"❌ Error scraping Instagram comments: {e}")
            return []
    
    def scrape_likes(self, post_url: str, max_likes: int = 100) -> List[str]:
        """
        Scrape likers from Instagram post
        
        Actor: datadoping/instagram-likes-scraper
        """
        logger.info(f"🔍 [Instagram] Scraping likes from: {post_url}")
        
        run_input = {
            "posts": [post_url],
            "max_count": max_likes
        }
        
        # Add cookie if available (CRITICAL for likes scraper)
        if self.session_cookie:
            run_input["cookies"] = [{"name": "sessionid", "value": self.session_cookie, "domain": ".instagram.com", "path": "/"}]
            run_input["sessionId"] = self.session_cookie
        
        try:
            # Run Instagram Likes Scraper
            run = self.client.actor("datadoping/instagram-likes-scraper").call(run_input=run_input)
            
            likers = []
            if run:
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    # Try multiple possible username fields
                    username = item.get('username') or item.get('user') or item.get('userName')
                    if username:
                        likers.append(username)
            
            logger.info(f"✓ Found {len(likers)} likers")
            
            return likers
        
        except Exception as e:
            logger.info(f"❌ Error scraping Instagram likes: {e}")
            return []


class LinkedInScraper:
    """
    LinkedIn scraper using the cookie-free supreme_coder/linkedin-post actor.
    A single deepScrape call returns both likers and commenters.
    Cost: ~$1 per 1,000 posts.  No cookies required.
    """

    def __init__(self, apify_client: ApifyClient, li_at_cookie: str = None):
        self.client = apify_client
        # Internal cache so reactions + comments share one API call
        self._cache: Dict[str, Dict] = {}

    # ── private: single API call, cached ──────────────────────────
    def _fetch_post_data(self, post_url: str) -> Dict:
        """
        Call supreme_coder/linkedin-post with deepScrape once per URL
        and cache the parsed likers / commenters lists.

        Response shape (confirmed):
          reactions[].profile.firstName / lastName / publicId
          comments[].author.firstName / lastName / publicId
        """
        if post_url in self._cache:
            logger.info(f"✓ [LinkedIn] Using cached data for: {post_url}")
            return self._cache[post_url]

        logger.info(f"🔍 [LinkedIn] Fetching post data via supreme_coder/linkedin-post: {post_url}")

        run_input = {
            "urls": [post_url],
            "limitPerSource": 1,
            "deepScrape": True,
            "rawData": False,
        }

        likers: List[str] = []
        commenters: List[str] = []

        try:
            run = self.client.actor("supreme_coder/linkedin-post").call(run_input=run_input)

            if run:
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    logger.info(f"📋 [LinkedIn] Dataset item keys: {list(item.keys())}")

                    # ── Extract likers from reactions[] ──
                    reactions = item.get("reactions") or []
                    if isinstance(reactions, list):
                        for r in reactions:
                            if not isinstance(r, dict):
                                continue
                            # Profile is nested: reactions[].profile.firstName/lastName
                            profile = r.get("profile") or r
                            first = profile.get("firstName", "")
                            last = profile.get("lastName", "")
                            full_name = f"{first} {last}".strip()
                            public_id = profile.get("publicId", "")

                            if full_name:
                                likers.append(full_name)

                    # ── Extract commenters from comments[] ──
                    comments = item.get("comments") or []
                    if isinstance(comments, list):
                        for c in comments:
                            if not isinstance(c, dict):
                                continue
                            # Author is nested: comments[].author.firstName/lastName
                            author = c.get("author") or {}
                            if isinstance(author, dict):
                                first = author.get("firstName", "")
                                last = author.get("lastName", "")
                                full_name = f"{first} {last}".strip()
                                public_id = author.get("publicId", "")

                                if full_name:
                                    commenters.append(full_name)

            logger.info(f"✓ [LinkedIn] {len(likers)} likers, {len(commenters)} commenters")

        except Exception as e:
            logger.error(f"❌ Error scraping LinkedIn post: {e}")

        result = {"likers": likers, "commenters": commenters}
        self._cache[post_url] = result
        return result

    # ── public API (signatures unchanged) ─────────────────────────
    def scrape_reactions(self, post_url: str, max_reactions: int = 100) -> List[str]:
        """Return list of liker / reactor names for a LinkedIn post."""
        data = self._fetch_post_data(post_url)
        return data["likers"][:max_reactions]

    def scrape_comments(self, post_url: str, max_comments: int = 100) -> List[str]:
        """Return list of commenter names for a LinkedIn post."""
        data = self._fetch_post_data(post_url)
        return data["commenters"][:max_comments]