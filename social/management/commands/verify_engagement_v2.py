"""
Django Management Command: Verify Engagement with Platform-Specific Scrapers

Usage:
    python manage.py verify_engagement_v2
    python manage.py verify_engagement_v2 --platform instagram
    python manage.py verify_engagement_v2 --post-id 123
    python manage.py verify_engagement_v2 --limit 10
"""

from django.core.management.base import BaseCommand
from utils.verification_service import VerificationService
import os


class Command(BaseCommand):
    help = 'Verify affiliate engagement using platform-specific Apify scrapers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            choices=['instagram', 'facebook', 'linkedin', 'all'],
            default='all',
            help='Platform to verify'
        )
        parser.add_argument(
            '--post-id',
            type=int,
            help='Verify specific post only'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of items to verify'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look back for unverified items'
        )

    def handle(self, *args, **options):
        platform = options['platform']
        post_id = options['post_id']
        limit = options['limit']
        days = options['days']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('PLATFORM-SPECIFIC APIFY VERIFICATION'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Initialize verification service
        try:
            service = VerificationService()
            self.stdout.write(self.style.SUCCESS('✓ Verification service initialized'))
            self.stdout.write(f'   Using proper Apify actors for each platform')
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'✗ {e}'))
            self.stdout.write(self.style.WARNING('\nPlease set APIFY_TOKEN in environment variables'))
            self.stdout.write(self.style.WARNING('Get your token from: https://console.apify.com/account/integrations'))
            return

        # Check for Instagram cookie
        if not os.getenv('INSTAGRAM_SESSION_COOKIE'):
            self.stdout.write(self.style.WARNING('\n⚠️  INSTAGRAM_SESSION_COOKIE not set'))
            self.stdout.write(self.style.WARNING('   Instagram like verification may be limited'))
            self.stdout.write(self.style.WARNING('   Set cookie for full liker list'))

        self.stdout.write('')

        # Verify specific post
        if post_id:
            self.stdout.write(f'Verifying post {post_id}...\n')
            
            if platform == 'all' or platform == 'instagram':
                self.stdout.write(self.style.SUCCESS('--- Instagram ---'))
                like_results = service.verify_likes_for_post(post_id, 'instagram')
                comment_results = service.verify_comments_for_post(post_id, 'instagram')
                self.stdout.write('')
            
            if platform == 'all' or platform == 'facebook':
                self.stdout.write(self.style.SUCCESS('--- Facebook ---'))
                like_results = service.verify_likes_for_post(post_id, 'facebook')
                comment_results = service.verify_comments_for_post(post_id, 'facebook')
                self.stdout.write('')
            
            if platform == 'all' or platform == 'linkedin':
                self.stdout.write(self.style.SUCCESS('--- LinkedIn ---'))
                like_results = service.verify_likes_for_post(post_id, 'linkedin')
                comment_results = service.verify_comments_for_post(post_id, 'linkedin')
                self.stdout.write('')
        
        # Verify recent engagement
        else:
            self.stdout.write(f'Verifying recent engagement (last {days} days, limit {limit})...\n')
            
            results = service.verify_all_recent_engagement(days=days, limit=limit)
            
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
            self.stdout.write(self.style.SUCCESS('VERIFICATION COMPLETE'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(f'\n📊 Summary:')
            self.stdout.write(f'   Likes checked: {results["total_likes_checked"]}')
            self.stdout.write(f'   ✓ Verified: {results["verified_likes"]}')
            self.stdout.write(f'   ✗ Failed: {results["failed_likes"]}')
            self.stdout.write(f'\n   Comments checked: {results["total_comments_checked"]}')
            self.stdout.write(f'   ✓ Verified: {results["verified_comments"]}')
            self.stdout.write(f'   ✗ Failed: {results["failed_comments"]}')
            self.stdout.write(f'\n   Total verified: {results["verified_likes"] + results["verified_comments"]}')
            self.stdout.write('')
