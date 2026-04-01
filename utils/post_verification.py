import logging
logger = logging.getLogger(__name__)

"""
Post Verification Service

Matches affiliate engagement against scraped data already in database
instead of making live API calls.
"""

from typing import Dict, List
from django.utils import timezone

from social.models import (
    Post, Like, Comment, AffiliateProfile,
    ScrapedPost, ScrapedLike, ScrapedComment
)


class PostVerificationService:
    """Service for verifying affiliates against scraped data"""
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name/username for matching (lowercase, trim)"""
        return name.lower().strip()
    
    def _check_match(self, search_name: str, scraped_names: List[str]) -> bool:
        """Check if search name matches any scraped name"""
        normalized_search = self._normalize_name(search_name)
        normalized_scraped = [self._normalize_name(name) for name in scraped_names]
        
        return normalized_search in normalized_scraped
    
    def verify_post_engagement(self, post_id: int, platform: str) -> Dict:
        """
        Verify all affiliates' engagement against scraped data
        
        Args:
            post_id: Post ID
            platform: 'instagram', 'facebook', or 'linkedin'
        
        Returns:
            Dictionary with verification results
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return {'success': False, 'error': 'Post not found'}
        
        # Check if post has been scraped
        try:
            scraped_post = ScrapedPost.objects.get(post=post, platform=platform)
        except ScrapedPost.DoesNotExist:
            return {
                'success': False,
                'error': f'Post has not been scraped for {platform}. Please scrape first.'
            }
        
        logger.info(f"📊 Verifying engagement for post {post_id} on {platform}")
        logger.info(f"   Scraped data: {scraped_post.total_likes_found} likes, {scraped_post.total_comments_found} comments")
        
        # Get scraped usernames
        scraped_likers = list(scraped_post.likes.values_list('username', flat=True))
        scraped_commenters = list(scraped_post.comments.values_list('username', flat=True))
        
        # Verify likes
        likes_to_verify = Like.objects.filter(
            post=post,
            platform=platform
        )
        
        verified_likes = 0
        failed_likes = 0
        
        for like in likes_to_verify:
            affiliate_username = like.affiliate.get_platform_username(platform)
            is_verified = self._check_match(affiliate_username, scraped_likers)
            
            # Update like record
            like.is_verified = is_verified
            like.verified_at = timezone.now()
            like.verification_method = 'apify_scraped'
            like.save()
            
            if is_verified:
                verified_likes += 1
                logger.info(f"  ✓ {affiliate_username} (like)")
            else:
                failed_likes += 1
                logger.info(f"  ✗ {affiliate_username} (like)")
        
        # Verify comments
        comments_to_verify = Comment.objects.filter(
            post=post,
            platform=platform
        )
        
        verified_comments = 0
        failed_comments = 0
        
        for comment in comments_to_verify:
            affiliate_username = comment.affiliate.get_platform_username(platform)
            is_verified = self._check_match(affiliate_username, scraped_commenters)
            
            # Update comment record
            comment.is_verified = is_verified
            comment.verified_at = timezone.now()
            comment.verification_method = 'apify_scraped'
            comment.save()
            
            if is_verified:
                verified_comments += 1
                logger.info(f"  ✓ {affiliate_username} (comment)")
            else:
                failed_comments += 1
                logger.info(f"  ✗ {affiliate_username} (comment)")
        
        result = {
            'success': True,
            'post_id': post_id,
            'platform': platform,
            'likes_checked': likes_to_verify.count(),
            'verified_likes': verified_likes,
            'failed_likes': failed_likes,
            'comments_checked': comments_to_verify.count(),
            'verified_comments': verified_comments,
            'failed_comments': failed_comments,
            'total_verified': verified_likes + verified_comments
        }
        
        logger.info(f"\n✓ Verification complete!")
        logger.info(f"  Likes: {verified_likes}/{likes_to_verify.count()} verified")
        logger.info(f"  Comments: {verified_comments}/{comments_to_verify.count()} verified")
        
        return result
