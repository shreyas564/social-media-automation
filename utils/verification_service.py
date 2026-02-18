"""
Django-integrated Verification Service

This module provides the main verification service that:
1. Uses platform-specific scrapers
2. Matches affiliate usernames
3. Saves verification results to database
4. Tracks Apify run IDs for audit trail
"""

import os
from typing import List, Dict, Optional
from django.utils import timezone
from apify_client import ApifyClient

from social.models import Like, Comment, Share, AffiliateProfile, Post
from utils.platform_scrapers import FacebookScraper, InstagramScraper, LinkedInScraper


class VerificationService:
    """Main service for verifying affiliate engagement"""
    
    def __init__(self, apify_token: str = None):
        """
        Initialize Apify client and platform scrapers
        
        Args:
            apify_token: Apify API token (or uses APIFY_TOKEN env var)
        """
        self.apify_token = apify_token or os.getenv('APIFY_TOKEN')
        if not self.apify_token:
            raise ValueError("Apify API token is required. Set APIFY_TOKEN environment variable.")
        
        self.client = ApifyClient(self.apify_token)
        
        # Initialize platform scrapers
        self.facebook = FacebookScraper(self.client)
        self.instagram = InstagramScraper(self.client)
        self.linkedin = LinkedInScraper(self.client)
        
        # Get Instagram session cookie if available
        instagram_cookie = os.getenv('INSTAGRAM_SESSION_COOKIE')
        if instagram_cookie:
            self.instagram.session_cookie = instagram_cookie
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name/username for matching (lowercase, trim)"""
        return name.lower().strip()
    
    def _check_match(self, search_name: str, scraped_names: List[str]) -> bool:
        """
        Check if search name matches any scraped name
        
        Args:
            search_name: Affiliate username/name to search for
            scraped_names: List of names from scraping
        
        Returns:
            True if match found
        """
        normalized_search = self._normalize_name(search_name)
        normalized_scraped = [self._normalize_name(name) for name in scraped_names]
        
        return normalized_search in normalized_scraped
    
    # ==================== VERIFY LIKES ====================
    
    def verify_like(self, like_id: int) -> bool:
        """
        Verify a single like record
        
        Args:
            like_id: ID of Like model instance
        
        Returns:
            True if verified, False otherwise
        """
        try:
            like = Like.objects.get(id=like_id)
        except Like.DoesNotExist:
            print(f"❌ Like {like_id} not found")
            return False
        
        # Get post URL for the platform
        post = like.post
        platform = like.platform
        
        if platform == 'instagram':
            post_url = post.Ipost_url
            if not post_url:
                print(f"❌ No Instagram URL for post {post.id}")
                return False
            
            likers = self.instagram.scrape_likes(post_url)
        
        elif platform == 'facebook':
            post_url = post.Fposturl
            if not post_url:
                print(f"❌ No Facebook URL for post {post.id}")
                return False
            
            likers = self.facebook.scrape_likes(post_url)
        
        elif platform == 'linkedin':
            post_url = post.Lposturl
            if not post_url:
                print(f"❌ No LinkedIn URL for post {post.id}")
                return False
            
            likers = self.linkedin.scrape_reactions(post_url)
        
        else:
            print(f"❌ Unknown platform: {platform}")
            return False
        
        # Check if affiliate's platform-specific username is in the likers list
        affiliate_username = like.affiliate.get_platform_username(platform)
        is_verified = self._check_match(affiliate_username, likers)
        
        # Save verification result to database
        like.is_verified = is_verified
        like.verified_at = timezone.now()
        like.verification_method = 'apify'
        like.save()
        
        status = "✓ VERIFIED" if is_verified else "✗ NOT VERIFIED"
        print(f"{status}: {affiliate_username} - Like on {platform}")
        
        return is_verified
    
    def verify_likes_for_post(self, post_id: int, platform: str) -> Dict[str, bool]:
        """
        Verify all likes for a specific post on a specific platform (BATCH - cost-effective)
        
        Args:
            post_id: Post ID
            platform: 'instagram', 'facebook', or 'linkedin'
        
        Returns:
            Dictionary mapping affiliate username to verification status
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            print(f"❌ Post {post_id} not found")
            return {}
        
        # Get all unverified likes for this post and platform
        likes = Like.objects.filter(
            post=post,
            platform=platform,
            is_verified=False
        )
        
        if not likes.exists():
            print(f"ℹ️ No unverified likes for post {post_id} on {platform}")
            return {}
        
        print(f"📊 Batch verifying {likes.count()} likes for post {post_id} on {platform}")
        
        # Get post URL
        if platform == 'instagram':
            post_url = post.Ipost_url
            likers = self.instagram.scrape_likes(post_url) if post_url else []
        
        elif platform == 'facebook':
            post_url = post.Fposturl
            likers = self.facebook.scrape_likes(post_url) if post_url else []
        
        elif platform == 'linkedin':
            post_url = post.Lposturl
            likers = self.linkedin.scrape_reactions(post_url) if post_url else []
        
        else:
            print(f"❌ Unknown platform: {platform}")
            return {}
        
        # Verify each like
        results = {}
        for like in likes:
            affiliate_username = like.affiliate.get_platform_username(platform)
            is_verified = self._check_match(affiliate_username, likers)
            
            # Save to database
            like.is_verified = is_verified
            like.verified_at = timezone.now()
            like.verification_method = 'apify'
            like.save()
            
            results[affiliate_username] = is_verified
            
            status = "✓" if is_verified else "✗"
            print(f"  {status} {affiliate_username}")
        
        return results
    
    # ==================== VERIFY COMMENTS ====================
    
    def verify_comment(self, comment_id: int) -> bool:
        """
        Verify a single comment record
        
        Args:
            comment_id: ID of Comment model instance
        
        Returns:
            True if verified, False otherwise
        """
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            print(f"❌ Comment {comment_id} not found")
            return False
        
        # Get post URL for the platform
        post = comment.post
        platform = comment.platform
        
        if platform == 'instagram':
            post_url = post.Ipost_url
            if not post_url:
                print(f"❌ No Instagram URL for post {post.id}")
                return False
            
            commenters = self.instagram.scrape_comments(post_url)
        
        elif platform == 'facebook':
            post_url = post.Fposturl
            if not post_url:
                print(f"❌ No Facebook URL for post {post.id}")
                return False
            
            commenters = self.facebook.scrape_comments(post_url)
        
        elif platform == 'linkedin':
            post_url = post.Lposturl
            if not post_url:
                print(f"❌ No LinkedIn URL for post {post.id}")
                return False
            
            commenters = self.linkedin.scrape_comments(post_url)
        
        else:
            print(f"❌ Unknown platform: {platform}")
            return False
        
        # Check if affiliate's platform-specific username is in the commenters list
        affiliate_username = comment.affiliate.get_platform_username(platform)
        is_verified = self._check_match(affiliate_username, commenters)
        
        # Save verification result to database
        comment.is_verified = is_verified
        comment.verified_at = timezone.now()
        comment.verification_method = 'apify'
        comment.save()
        
        status = "✓ VERIFIED" if is_verified else "✗ NOT VERIFIED"
        print(f"{status}: {affiliate_username} - Comment on {platform}")
        
        return is_verified
    
    def verify_comments_for_post(self, post_id: int, platform: str) -> Dict[str, bool]:
        """
        Verify all comments for a specific post on a specific platform (BATCH - cost-effective)
        
        Args:
            post_id: Post ID
            platform: 'instagram', 'facebook', or 'linkedin'
        
        Returns:
            Dictionary mapping affiliate username to verification status
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            print(f"❌ Post {post_id} not found")
            return {}
        
        # Get all unverified comments for this post and platform
        comments = Comment.objects.filter(
            post=post,
            platform=platform,
            is_verified=False
        )
        
        if not comments.exists():
            print(f"ℹ️ No unverified comments for post {post_id} on {platform}")
            return {}
        
        print(f"📊 Batch verifying {comments.count()} comments for post {post_id} on {platform}")
        
        # Get post URL and scrape
        if platform == 'instagram':
            post_url = post.Ipost_url
            commenters = self.instagram.scrape_comments(post_url) if post_url else []
        
        elif platform == 'facebook':
            post_url = post.Fposturl
            commenters = self.facebook.scrape_comments(post_url) if post_url else []
        
        elif platform == 'linkedin':
            post_url = post.Lposturl
            commenters = self.linkedin.scrape_comments(post_url) if post_url else []
        
        else:
            print(f"❌ Unknown platform: {platform}")
            return {}
        
        # Verify each comment
        results = {}
        for comment in comments:
            affiliate_username = comment.affiliate.get_platform_username(platform)
            is_verified = self._check_match(affiliate_username, commenters)
            
            # Save to database
            comment.is_verified = is_verified
            comment.verified_at = timezone.now()
            comment.verification_method = 'apify'
            comment.save()
            
            results[affiliate_username] = is_verified
            
            status = "✓" if is_verified else "✗"
            print(f"  {status} {affiliate_username}")
        
        return results
    
    # ==================== BULK VERIFICATION ====================
    
    def verify_all_recent_engagement(self, days: int = 7, limit: int = 50) -> Dict[str, int]:
        """
        Verify all recent unverified engagement (last N days)
        
        Args:
            days: Number of days to look back
            limit: Maximum number of items to verify
        
        Returns:
            Summary statistics
        """
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get unverified likes
        unverified_likes = Like.objects.filter(
            is_verified=False,
            created_at__gte=cutoff_date
        )[:limit]
        
        # Get unverified comments
        unverified_comments = Comment.objects.filter(
            is_verified=False,
            created_at__gte=cutoff_date
        )[:limit]
        
        print(f"📊 Verifying {unverified_likes.count()} likes and {unverified_comments.count()} comments from last {days} days")
        
        verified_likes = 0
        verified_comments = 0
        
        # Group by post and platform for batch processing
        # This is more cost-effective than verifying one by one
        
        # Process likes
        like_groups = {}
        for like in unverified_likes:
            key = (like.post.id, like.platform)
            if key not in like_groups:
                like_groups[key] = []
            like_groups[key].append(like)
        
        for (post_id, platform), likes in like_groups.items():
            results = self.verify_likes_for_post(post_id, platform)
            verified_likes += sum(1 for v in results.values() if v)
        
        # Process comments
        comment_groups = {}
        for comment in unverified_comments:
            key = (comment.post.id, comment.platform)
            if key not in comment_groups:
                comment_groups[key] = []
            comment_groups[key].append(comment)
        
        for (post_id, platform), comments in comment_groups.items():
            results = self.verify_comments_for_post(post_id, platform)
            verified_comments += sum(1 for v in results.values() if v)
        
        return {
            'total_likes_checked': unverified_likes.count(),
            'total_comments_checked': unverified_comments.count(),
            'verified_likes': verified_likes,
            'verified_comments': verified_comments,
            'failed_likes': unverified_likes.count() - verified_likes,
            'failed_comments': unverified_comments.count() - verified_comments
        }
