"""
Apify Engagement Verification Service

This module provides functions to scrape social media posts using Apify
and verify if affiliate users actually liked or commented on posts.

Cost-saving features:
- Only scrapes when verification is needed
- Caches results to avoid duplicate scraping
- Checks only for specific affiliate usernames
- Batch processing support
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from apify_client import ApifyClient


class ApifyVerificationService:
    """Service to verify affiliate engagement using Apify scrapers"""
    
    def __init__(self, api_token: str = None):
        """
        Initialize Apify client
        
        Args:
            api_token: Apify API token (or uses APIFY_TOKEN env var)
        """
        self.api_token = api_token or os.getenv('APIFY_TOKEN')
        if not self.api_token:
            raise ValueError("Apify API token is required")
        
        self.client = ApifyClient(self.api_token)
        
        # Cache to avoid re-scraping same posts
        self.cache = {}
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
    
    def _get_cache_key(self, url: str, data_type: str) -> str:
        """Generate cache key for post URL and data type"""
        return f"{url}:{data_type}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp')
        if not cached_time:
            return False
        
        age = datetime.now() - cached_time
        return age < self.cache_duration
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[str]]:
        """Retrieve data from cache if valid"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key].get('data')
        return None
    
    def _save_to_cache(self, cache_key: str, data: List[str]):
        """Save data to cache"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    # ==================== INSTAGRAM ====================
    
    def scrape_instagram_post(self, post_url: str) -> Dict[str, List[str]]:
        """
        Scrape Instagram post to get list of users who liked and commented
        
        Args:
            post_url: Instagram post URL (e.g., https://www.instagram.com/p/ABC123/)
        
        Returns:
            {
                'likers': ['username1', 'username2', ...],
                'commenters': ['username3', 'username4', ...]
            }
        """
        print(f"🔍 Scraping Instagram post: {post_url}")
        
        # Check cache first
        cache_key_likes = self._get_cache_key(post_url, 'instagram_likes')
        cache_key_comments = self._get_cache_key(post_url, 'instagram_comments')
        
        cached_likes = self._get_from_cache(cache_key_likes)
        cached_comments = self._get_from_cache(cache_key_comments)
        
        if cached_likes is not None and cached_comments is not None:
            print("✓ Using cached data")
            return {
                'likers': cached_likes,
                'commenters': cached_comments
            }
        
        # 1. Scrape Likes using datadoping/instagram-likes-scraper
        likers = []
        try:
            print(f"🔍 [Instagram] Scraping likes using 'datadoping/instagram-likes-scraper'")
            run_input_likes = {
                "posts": [post_url],
                "max_count": 1000  # Reasonable limit
            }
            # Add cookie if APIFY_TOKEN is set as env var but maybe session cookie is needed?
            # The original class didn't have session cookie passed in __init__, but it might be in env?
            # Ideally verification service should have access to cookies or be robust.
            # defaulting to just token auth for now.
            
            run_likes = self.client.actor("datadoping/instagram-likes-scraper").call(run_input=run_input_likes)
            
            if run_likes:
                for item in self.client.dataset(run_likes["defaultDatasetId"]).iterate_items():
                    username = item.get('username') or item.get('user') or item.get('userName')
                    if username:
                        likers.append(username)
            print(f"✓ Found {len(likers)} likers")
            
        except Exception as e:
            print(f"❌ Error scraping Instagram likes: {e}")

        # 2. Scrape Comments using datadoping/instagram-comments-and-replies-scraper
        commenters = []
        try:
            print(f"🔍 [Instagram] Scraping comments using 'datadoping/instagram-comments-and-replies-scraper'")
            run_input_comments = {
                "code_or_id_or_url": [post_url],
                "resultsLimit": 100
            }
            
            run_comments = self.client.actor("datadoping/instagram-comments-and-replies-scraper").call(run_input=run_input_comments)
            
            if run_comments:
                for item in self.client.dataset(run_comments["defaultDatasetId"]).iterate_items():
                    # Filter out captions based on type/content_type
                    # Screenshot shows "Type" column with "caption"
                    item_type = item.get('type') or item.get('content_type')
                    if item_type == 'caption':
                        continue

                    username = item.get('username') or item.get('ownerUsername')
                    if username:
                        commenters.append(username)
            print(f"✓ Found {len(commenters)} commenters")

        except Exception as e:
            print(f"❌ Error scraping Instagram comments: {e}")
            
        # Save to cache
        self._save_to_cache(cache_key_likes, likers)
        self._save_to_cache(cache_key_comments, commenters)
        
        return {
            'likers': likers,
            'commenters': commenters
        }
    
    # ==================== FACEBOOK ====================
    
    def scrape_facebook_post(self, post_url: str) -> Dict[str, List[str]]:
        """
        Scrape Facebook post to get list of users who liked and commented
        
        Args:
            post_url: Facebook post URL
        
        Returns:
            {
                'likers': ['username1', 'username2', ...],
                'commenters': ['username3', 'username4', ...]
            }
        """
        print(f"🔍 Scraping Facebook post: {post_url}")
        
        # Check cache
        cache_key_likes = self._get_cache_key(post_url, 'facebook_likes')
        cache_key_comments = self._get_cache_key(post_url, 'facebook_comments')
        
        cached_likes = self._get_from_cache(cache_key_likes)
        cached_comments = self._get_from_cache(cache_key_comments)
        
        if cached_likes is not None and cached_comments is not None:
            print("✓ Using cached data")
            return {
                'likers': cached_likes,
                'commenters': cached_comments
            }
        
        # Apify Facebook Scraper Actor
        # Actor ID: thedoor/facebook-comment-scraper
        run_input = {
            "postUrls": [post_url],
            "maxComments": 100,  # Fetch up to 100 comments
            "commentsMode": "RANKED_THREADED"
        }
        
        try:
            print(f"🔍 [Facebook] Using 'thedoor/facebook-comment-scraper' for: {post_url}")
            run = self.client.actor("thedoor/facebook-comment-scraper").call(run_input=run_input)
            
            likers = []
            commenters = []
            
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                # The 'thedoor' scraper returns individual comment items, not a post object with a list
                # Check multiple fields for author name
                author_name = (
                    item.get('author_name') or # 'thedoor' uses snake_case
                    item.get('name') or 
                    item.get('userName') or 
                    item.get('authorName') or 
                    item.get('author')
                )
                
                if author_name:
                    commenters.append(author_name)
            
            # Save to cache
            self._save_to_cache(cache_key_likes, likers)
            self._save_to_cache(cache_key_comments, commenters)
            
            print(f"✓ Found {len(commenters)} commenters (likes not publicly available)")
            
            return {
                'likers': likers,  # Usually empty - FB doesn't expose this
                'commenters': commenters
            }
        
        except Exception as e:
            print(f"❌ Error scraping Facebook: {e}")
            return {
                'likers': [],
                'commenters': []
            }
    
    # ==================== LINKEDIN ====================
    
    def scrape_linkedin_post(self, post_url: str) -> Dict[str, List[str]]:
        """
        Scrape LinkedIn post to get list of users who liked and commented
        
        Args:
            post_url: LinkedIn post URL
        
        Returns:
            {
                'likers': ['Name1', 'Name2', ...],
                'commenters': ['Name3', 'Name4', ...]
            }
        """
        print(f"🔍 Scraping LinkedIn post: {post_url}")
        
        # Check cache
        cache_key_likes = self._get_cache_key(post_url, 'linkedin_likes')
        cache_key_comments = self._get_cache_key(post_url, 'linkedin_comments')
        
        cached_likes = self._get_from_cache(cache_key_likes)
        cached_comments = self._get_from_cache(cache_key_comments)
        
        if cached_likes is not None and cached_comments is not None:
            print("✓ Using cached data")
            return {
                'likers': cached_likes,
                'commenters': cached_comments
            }
        
        # Note: LinkedIn scraping is more restricted
        # You may need a custom solution or different actor
        
        print("⚠️ LinkedIn scraping has limited support")
        
        return {
            'likers': [],
            'commenters': []
        }
    
    # ==================== VERIFICATION LOGIC ====================
    
    def verify_like(self, post_url: str, username: str, platform: str) -> bool:
        """
        Verify if a specific username liked a post
        
        Args:
            post_url: Post URL
            username: Affiliate username to check
            platform: 'instagram', 'facebook', or 'linkedin'
        
        Returns:
            True if username found in likers list, False otherwise
        """
        platform = platform.lower()
        
        if platform == 'instagram':
            data = self.scrape_instagram_post(post_url)
        elif platform == 'facebook':
            data = self.scrape_facebook_post(post_url)
        elif platform == 'linkedin':
            data = self.scrape_linkedin_post(post_url)
        else:
            print(f"❌ Unknown platform: {platform}")
            return False
        
        likers = data.get('likers', [])
        
        # Case-insensitive match
        username_lower = username.lower()
        found = any(liker.lower() == username_lower for liker in likers)
        
        if found:
            print(f"✓ {username} VERIFIED as liker")
        else:
            print(f"✗ {username} NOT found in likers")
        
        return found
    
    def verify_comment(self, post_url: str, username: str, platform: str, comment_text: str = None) -> bool:
        """
        Verify if a specific username commented on a post
        
        Args:
            post_url: Post URL
            username: Affiliate username to check
            platform: 'instagram', 'facebook', or 'linkedin'
            comment_text: Optional - specific comment text to verify
        
        Returns:
            True if username found in commenters list, False otherwise
        """
        platform = platform.lower()
        
        if platform == 'instagram':
            data = self.scrape_instagram_post(post_url)
        elif platform == 'facebook':
            data = self.scrape_facebook_post(post_url)
        elif platform == 'linkedin':
            data = self.scrape_linkedin_post(post_url)
        else:
            print(f"❌ Unknown platform: {platform}")
            return False
        
        commenters = data.get('commenters', [])
        
        # Case-insensitive match
        username_lower = username.lower()
        found = any(commenter.lower() == username_lower for commenter in commenters)
        
        if found:
            print(f"✓ {username} VERIFIED as commenter")
        else:
            print(f"✗ {username} NOT found in commenters")
        
        return found
    
    # ==================== BATCH VERIFICATION ====================
    
    def verify_multiple_users(self, post_url: str, usernames: List[str], platform: str, action: str = 'like') -> Dict[str, bool]:
        """
        Verify multiple usernames at once (cost-effective - single scrape)
        
        Args:
            post_url: Post URL
            usernames: List of affiliate usernames to check
            platform: 'instagram', 'facebook', or 'linkedin'
            action: 'like' or 'comment'
        
        Returns:
            Dictionary mapping username to verification status
            {'username1': True, 'username2': False, ...}
        """
        print(f"🔍 Batch verifying {len(usernames)} users for {action} on {platform}")
        
        platform = platform.lower()
        
        # Single scrape for all users
        if platform == 'instagram':
            data = self.scrape_instagram_post(post_url)
        elif platform == 'facebook':
            data = self.scrape_facebook_post(post_url)
        elif platform == 'linkedin':
            data = self.scrape_linkedin_post(post_url)
        else:
            return {username: False for username in usernames}
        
        # Get appropriate list
        if action == 'like':
            users_list = data.get('likers', [])
        else:
            users_list = data.get('commenters', [])
        
        # Convert to lowercase for matching
        users_list_lower = [u.lower() for u in users_list]
        
        # Check each username
        results = {}
        for username in usernames:
            found = username.lower() in users_list_lower
            results[username] = found
            
            status = "✓" if found else "✗"
            print(f"  {status} {username}")
        
        return results


# ==================== COST-SAVING UTILITIES ====================

def get_pending_verifications(limit: int = 50):
    """
    Get list of likes/comments that need verification
    Only returns recent items to limit scraping costs
    
    Args:
        limit: Maximum number of items to verify at once
    
    Returns:
        List of (Like/Comment object, post_url, username, platform) tuples
    """
    from social.models import Like, Comment, Post
    from datetime import datetime, timedelta
    
    # Only verify items from last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    
    pending_likes = Like.objects.filter(
        is_verified=False,
        created_at__gte=week_ago
    ).select_related('post', 'affiliate')[:limit]
    
    pending_comments = Comment.objects.filter(
        is_verified=False,
        created_at__gte=week_ago
    ).select_related('post', 'affiliate')[:limit]
    
    return {
        'likes': pending_likes,
        'comments': pending_comments
    }


def estimate_scraping_cost(num_posts: int) -> float:
    """
    Estimate Apify cost for scraping
    
    Args:
        num_posts: Number of posts to scrape
    
    Returns:
        Estimated cost in USD
    """
    # Apify pricing (approximate):
    # Instagram: ~$0.001-0.01 per post
    # Facebook: ~$0.01-0.05 per post
    
    avg_cost_per_post = 0.02  # Conservative estimate
    return num_posts * avg_cost_per_post
