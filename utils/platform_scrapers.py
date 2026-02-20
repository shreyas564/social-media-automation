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
        print(f"🔍 [Facebook] Scraping comments from: {post_url}")
        
        run_input = {
            "postUrls": [post_url],
            "maxComments": max_comments,
            "commentsMode": "RANKED_THREADED"
        }
        
        try:
            # Run Facebook Comments Scraper
            # User requested 'thedoor/facebook-comment-scraper'
            print(f"🔍 [Facebook] Using 'thedoor/facebook-comment-scraper' for: {post_url}")
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
            
            print(f"✓ Found {len(commenters)} commenters")
            return commenters
        
        except Exception as e:
            print(f"❌ Error scraping Facebook comments: {e}")
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
        print(f"🔍 [Facebook] Scraping likes from: {post_url}")
        
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
            
            print(f"✓ Found {len(likers)} likers")
            return likers
        
        except Exception as e:
            print(f"❌ Error scraping Facebook likes: {e}")
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
        print(f"🔍 [Instagram] Scraping comments from: {post_url}")
        
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
                        
            print(f"✓ Found {len(commenters)} commenters")
            return commenters
        
        except Exception as e:
            print(f"❌ Error scraping Instagram comments: {e}")
            return []
    
    def scrape_likes(self, post_url: str, max_likes: int = 100) -> List[str]:
        """
        Scrape likers from Instagram post
        
        Actor: datadoping/instagram-likes-scraper
        """
        print(f"🔍 [Instagram] Scraping likes from: {post_url}")
        
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
            
            print(f"✓ Found {len(likers)} likers")
            
            return likers
        
        except Exception as e:
            print(f"❌ Error scraping Instagram likes: {e}")
            return []


class LinkedInScraper:
    """LinkedIn-specific scrapers using proper Apify actors"""
    
    def __init__(self, apify_client: ApifyClient, li_at_cookie: str = None):
        self.client = apify_client
        self.cookie = li_at_cookie
    
    def scrape_reactions(self, post_url: str, max_reactions: int = 100) -> List[str]:
        """
        Scrape reactions (likers) from LinkedIn post
        
        Actor: harvestapi/linkedin-post-reactions
        """
        print(f"🔍 [LinkedIn] Scraping reactions from: {post_url}")
        
        run_input = {
            "urls": [post_url],
        }
        
        # Add cookie if available
        if self.cookie:
             run_input["cookies"] = [{"name": "li_at", "value": self.cookie, "domain": ".linkedin.com", "path": "/"}]
        
        try:
            # Run LinkedIn Reactions Scraper
            run = self.client.actor("harvestapi/linkedin-post-reactions").call(run_input=run_input)
            
            reactors = []
            if run:
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    # harvestapi usually returns 'name' or 'profile_url'
                    name = item.get('name') or item.get('title')
                    if name:
                        reactors.append(name)
                        
            print(f"✓ Found {len(reactors)} reactors")
            return reactors
        
        except Exception as e:
            print(f"❌ Error scraping LinkedIn reactions: {e}")
            return []

    def scrape_comments(self, post_url: str, max_comments: int = 100) -> List[str]:
        """
        Scrape commenters from LinkedIn post
        
        Actor: harvestapi/linkedin-post-comments
        """
        print(f"🔍 [LinkedIn] Scraping comments from: {post_url}")
        
        run_input = {
            "urls": [post_url],
        }
        
        if self.cookie:
            run_input["cookies"] = [{"name": "li_at", "value": self.cookie, "domain": ".linkedin.com", "path": "/"}]
        
        try:
            # Run LinkedIn Comments Scraper
            run = self.client.actor("harvestapi/linkedin-post-comments").call(run_input=run_input)
            
            commenters = []
            if run:
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    # Extract author name
                    author_name = item.get('author_name') or item.get('name') or item.get('author', {}).get('name')
                    if author_name:
                        commenters.append(author_name)
            
            print(f"✓ Found {len(commenters)} commenters")
            return commenters
        
        except Exception as e:
            print(f"❌ Error scraping LinkedIn comments: {e}")
            return []