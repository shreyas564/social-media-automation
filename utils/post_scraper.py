import logging
logger = logging.getLogger(__name__)

"""
Post-Wise Scraping Service

This module scrapes entire posts at once and saves all engagement data 
(likes, comments) to the database for later verification matching.
"""

import os
from typing import Dict
from django.utils import timezone
from apify_client import ApifyClient

from social.models import Post, ScrapedPost, ScrapedLike, ScrapedComment
from utils.platform_scrapers import FacebookScraper, InstagramScraper, LinkedInScraper


class PostScrapingService:
    """Service for scraping posts and storing engagement data"""
    
    def __init__(self, apify_token: str = None):
        """Initialize Apify client and scrapers"""
        self.apify_token = apify_token or os.getenv('APIFY_TOKEN')
        if not self.apify_token:
            raise ValueError("Apify API token is required")
        
        self.client = ApifyClient(self.apify_token)
        
        # Initialize platform scrapers
        self.facebook = FacebookScraper(self.client)
        self.instagram = InstagramScraper(self.client)
        self.linkedin = LinkedInScraper(self.client)
        
        # Get Instagram session cookie if available
        instagram_cookie = os.getenv('INSTAGRAM_SESSION_COOKIE')
        if instagram_cookie:
            self.instagram.session_cookie = instagram_cookie
    
    def scrape_post(self, post_id: int, platform: str, max_results: int = 500) -> Dict:
        """
        Scrape a post and save all engagement data to database
        
        Args:
            post_id: Post ID to scrape
            platform: 'instagram', 'facebook', or 'linkedin'
            max_results: Maximum number of likes/comments to fetch
        
        Returns:
            Dictionary with scraping results
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            logger.info(f"❌ Post {post_id} not found")
            return {'success': False, 'error': 'Post not found'}
        
        # Get post URL
        if platform == 'instagram':
            post_url = post.Ipost_url
        elif platform == 'facebook':
            post_url = post.Fposturl
        elif platform == 'linkedin':
            post_url = post.Lposturl
        else:
            return {'success': False, 'error': f'Unknown platform: {platform}'}
        
        if not post_url:
            return {'success': False, 'error': f'No {platform} URL for post {post_id}'}
        
        logger.info(f"🔍 Scraping {platform} post: {post_url}")
        
        # Scrape likes and comments
        likers = []
        commenters = []
        
        try:
            if platform == 'instagram':
                likers = self.instagram.scrape_likes(post_url, max_likes=max_results)
                commenters = self.instagram.scrape_comments(post_url, max_comments=max_results)
            
            elif platform == 'facebook':
                likers = self.facebook.scrape_likes(post_url, max_likes=max_results)
                commenters = self.facebook.scrape_comments(post_url, max_comments=max_results)
            
            elif platform == 'linkedin':
                likers = self.linkedin.scrape_reactions(post_url, max_reactions=max_results)
                commenters = self.linkedin.scrape_comments(post_url, max_comments=max_results)
        
        except Exception as e:
            logger.info(f"❌ Scraping error: {e}")
            return {'success': False, 'error': str(e)}
        
        # Save to database
        scraped_post, created = ScrapedPost.objects.update_or_create(
            post=post,
            platform=platform,
            defaults={
                'total_likes_found': len(likers),
                'total_comments_found': len(commenters),
                'scraped_at': timezone.now()
            }
        )
        
        # Clear old data if re-scraping
        if not created:
            scraped_post.likes.all().delete()
            scraped_post.comments.all().delete()
        
        # Save likes
        for username in likers:
            ScrapedLike.objects.create(
                scraped_post=scraped_post,
                username=username
            )
        
        # Save comments
        for username in commenters:
            ScrapedComment.objects.create(
                scraped_post=scraped_post,
                username=username
            )
        
        result = {
            'success': True,
            'platform': platform,
            'post_id': post_id,
            'likes_found': len(likers),
            'comments_found': len(commenters),
            'scraped_at': scraped_post.scraped_at,
            'was_updated': not created
        }
        
        logger.info(f"✓ Saved {len(likers)} likes and {len(commenters)} comments to database")
        
        return result
    
    def get_scrape_status(self, post_id: int, platform: str) -> Dict:
        """Check if a post has been scraped"""
        try:
            scraped = ScrapedPost.objects.get(post_id=post_id, platform=platform)
            return {
                'is_scraped': True,
                'scraped_at': scraped.scraped_at,
                'likes_count': scraped.total_likes_found,
                'comments_count': scraped.total_comments_found
            }
        except ScrapedPost.DoesNotExist:
            return {'is_scraped': False}
