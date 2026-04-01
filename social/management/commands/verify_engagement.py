"""
Django Management Command to Verify Affiliate Engagement Using Apify

Usage:
    python manage.py verify_engagement --platform instagram --limit 10
    python manage.py verify_engagement --all
    python manage.py verify_engagement --post-id 123
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from social.models import Like, Comment, Post, AffiliateProfile
from utils.apify_verification import ApifyVerificationService
import os


class Command(BaseCommand):
    help = 'Verify affiliate engagement using Apify scraping'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            choices=['instagram', 'facebook', 'linkedin', 'all'],
            default='all',
            help='Platform to verify'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of items to verify'
        )
        parser.add_argument(
            '--post-id',
            type=int,
            help='Verify specific post only'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be verified without actually scraping'
        )

    def handle(self, *args, **options):
        platform = options['platform']
        limit = options['limit']
        post_id = options['post_id']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('APIFY ENGAGEMENT VERIFICATION'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Initialize Apify service
        try:
            apify = ApifyVerificationService()
            self.stdout.write(self.style.SUCCESS('✓ Apify client initialized'))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'✗ {e}'))
            self.stdout.write(self.style.WARNING('Please set APIFY_TOKEN in environment variables'))
            return

        # Get pending verifications
        if post_id:
            # Verify specific post
            try:
                post = Post.objects.get(id=post_id)
                pending_likes = Like.objects.filter(post=post, is_verified=False)
                pending_comments = Comment.objects.filter(post=post, is_verified=False)
            except Post.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ Post {post_id} not found'))
                return
        else:
            # Get recent unverified items
            from datetime import timedelta
            from django.utils import timezone
            
            week_ago = timezone.now() - timedelta(days=7)
            
            if platform == 'all':
                pending_likes = Like.objects.filter(
                    is_verified=False,
                    created_at__gte=week_ago
                ).select_related('post', 'affiliate')[:limit]
                
                pending_comments = Comment.objects.filter(
                    is_verified=False,
                    created_at__gte=week_ago
                ).select_related('post', 'affiliate')[:limit]
            else:
                pending_likes = Like.objects.filter(
                    is_verified=False,
                    created_at__gte=week_ago,
                    platform=platform
                ).select_related('post', 'affiliate')[:limit]
                
                pending_comments = Comment.objects.filter(
                    is_verified=False,
                    created_at__gte=week_ago,
                    platform=platform
                ).select_related('post', 'affiliate')[:limit]

        total_likes = pending_likes.count()
        total_comments = pending_comments.count()
        
        self.stdout.write(f'\nFound {total_likes} likes and {total_comments} comments to verify')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN - Not actually scraping'))
            self.stdout.write(f'Would verify {total_likes + total_comments} items')
            return

        # Group by post for batch verification (cost-effective)
        posts_to_verify = {}
        
        for like in pending_likes:
            post_key = (like.post.id, like.platform)
            if post_key not in posts_to_verify:
                posts_to_verify[post_key] = {
                    'post': like.post,
                    'platform': like.platform,
                    'likes': [],
                    'comments': []
                }
            posts_to_verify[post_key]['likes'].append(like)

        for comment in pending_comments:
            post_key = (comment.post.id, comment.platform)
            if post_key not in posts_to_verify:
                posts_to_verify[post_key] = {
                    'post': comment.post,
                    'platform': comment.platform,
                    'likes': [],
                    'comments': []
                }
            posts_to_verify[post_key]['comments'].append(comment)

        self.stdout.write(f'\nVerifying {len(posts_to_verify)} unique posts')
        self.stdout.write(self.style.WARNING('This will consume Apify credits!\n'))

        verified_count = 0
        failed_count = 0

        # Verify each post
        for post_key, data in posts_to_verify.items():
            post = data['post']
            platform_name = data['platform']
            
            # Get appropriate post URL
            if platform_name == 'instagram':
                post_url = post.Ipost_url
            elif platform_name == 'facebook':
                post_url = post.Fposturl
            elif platform_name == 'linkedin':
                post_url = post.Lposturl
            else:
                continue

            if not post_url:
                self.stdout.write(self.style.WARNING(f'⚠ No URL for {platform_name} post {post.id}'))
                continue

            self.stdout.write(f'\n📍 Post {post.id} on {platform_name.upper()}')
            self.stdout.write(f'   URL: {post_url}')

            # Verify likes for this post
            if data['likes']:
                usernames = [like.affiliate.username for like in data['likes']]
                self.stdout.write(f'   Verifying {len(usernames)} likes...')
                
                try:
                    results = apify.verify_multiple_users(post_url, usernames, platform_name, 'like')
                    
                    for like in data['likes']:
                        is_valid = results.get(like.affiliate.username, False)
                        like.is_verified = is_valid
                        like.verified_at = timezone.now()
                        like.save()
                        
                        if is_valid:
                            verified_count += 1
                            self.stdout.write(f'     ✓ {like.affiliate.username}')
                        else:
                            failed_count += 1
                            self.stdout.write(self.style.WARNING(f'     ✗ {like.affiliate.username}'))
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'     Error: {e}'))

            # Verify comments for this post
            if data['comments']:
                usernames = [comment.affiliate.username for comment in data['comments']]
                self.stdout.write(f'   Verifying {len(usernames)} comments...')
                
                try:
                    results = apify.verify_multiple_users(post_url, usernames, platform_name, 'comment')
                    
                    for comment in data['comments']:
                        is_valid = results.get(comment.affiliate.username, False)
                        comment.is_verified = is_valid
                        comment.verified_at = timezone.now()
                        comment.save()
                        
                        if is_valid:
                            verified_count += 1
                            self.stdout.write(f'     ✓ {comment.affiliate.username}')
                        else:
                            failed_count += 1
                            self.stdout.write(self.style.WARNING(f'     ✗ {comment.affiliate.username}'))
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'     Error: {e}'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('VERIFICATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'✓ Verified: {verified_count}')
        self.stdout.write(self.style.WARNING(f'✗ Failed: {failed_count}'))
        self.stdout.write(f'📊 Total processed: {verified_count + failed_count}')
