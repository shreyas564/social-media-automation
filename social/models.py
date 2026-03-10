from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.
class SuperAdmin(models.Model):
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee (₹)'),
        ('USD', 'US Dollar ($)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='super_admin')
    name = models.CharField(max_length=100)
    minimum_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=0.01)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    fbtoken=models.CharField(max_length=300,blank=True, null=True)
    instatoken=models.CharField(max_length=300,blank=True, null=True)
    lntoken=models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

    @property
    def currency_symbol(self):
        return '₹' if self.currency == 'INR' else '$'


class Pages(models.Model):
    pageId=models.CharField( max_length=500,blank=True,null=True)
    pageName=models.CharField(blank=True,null=True)
    def __str__(self) -> str:
        return f"Page ID {self.pageId}"

class Post(models.Model):
    video = models.FileField(upload_to="post_videos/", blank=True, null=True)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    media_url=models.URLField(max_length=800, blank=True, null=True)
    media_type=models.CharField(max_length=100,choices=
    [("image","Image"),("video","Video")], default="image")
    caption = models.TextField()
    
    post_name=models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(SuperAdmin, on_delete=models.CASCADE)
    instapostid=models.CharField(max_length=300, blank=True, null=True)
    fbpostid=models.CharField(max_length=300, blank=True, null=True)
    lnpostid=models.CharField(max_length=300, blank=True, null=True)
    total_likes=models.IntegerField(default=0)
    total_comments=models.IntegerField(default=0)
    total_shares=models.IntegerField(default=0)
    ig_likes = models.IntegerField(default=0)
    ig_comments = models.IntegerField(default=0)
    ig_shares = models.CharField(max_length=20, default="NA")
    fb_likes = models.IntegerField(default=0)
    fb_comments = models.IntegerField(default=0)
    fb_shares = models.IntegerField(default=0)
    li_likes = models.IntegerField(default=0)
    li_comments = models.IntegerField(default=0)
    li_shares = models.IntegerField(default=0)

    Ipost_url=models.URLField(max_length=800, blank=True, null=True)
    Fposturl=models.URLField(max_length=800, blank=True, null=True) 
    Lposturl=models.URLField(max_length=800, blank=True, null=True) 

   # pageId=models.ForeignKey(Pages,on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Post  - {self.caption[:20]}"


#affiliated user regestration  for  storing in database
class AffiliateProfile(models.Model):
    username = models.CharField(max_length=150,unique=True)
    password = models.CharField(max_length=255)

    instagram_secret = models.CharField(max_length=255)
    linkedin_secret = models.CharField(max_length=255)
    facebook_secret = models.CharField(max_length=255)
    twitter_secret = models.CharField(max_length=255)
    
    # Platform-specific usernames for Apify verification
    instagram_username = models.CharField(max_length=150, blank=True, null=True, help_text="Instagram username for verification")
    facebook_username = models.CharField(max_length=150, blank=True, null=True, help_text="Facebook name/username for verification")
    linkedin_username = models.CharField(max_length=150, blank=True, null=True, help_text="LinkedIn name for verification")

    # Social Connect — OAuth status
    instagram_connected = models.BooleanField(default=False)
    facebook_connected = models.BooleanField(default=False)
    linkedin_connected = models.BooleanField(default=False)

    # Access tokens (stored for future API use, e.g. verification)
    instagram_access_token = models.TextField(blank=True, null=True)
    facebook_access_token = models.TextField(blank=True, null=True)
    linkedin_access_token = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    def get_platform_username(self, platform):
        """Get the appropriate username for the given platform"""
        if platform == 'instagram':
            return self.instagram_username or self.username
        elif platform == 'facebook':
            return self.facebook_username or self.username
        elif platform == 'linkedin':
            return self.linkedin_username or self.username
        return self.username
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    PLATFORM_CHOICES = [
    ('instagram', 'Instagram'),
    ('facebook', 'Facebook'),
    ('linkedin', 'LinkedIn')]

    platform = models.CharField(max_length=20,choices=PLATFORM_CHOICES,default='instagram',null=True,blank=True)
    
    # Verification fields
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(max_length=50, null=True, blank=True)  # 'apify', 'manual', 'screenshot'
    apify_run_id = models.CharField(max_length=100, null=True, blank=True)  # Audit trail

    def __str__(self):
        return f"Comment by {self.affiliate.username} on Post {self.post.id}" # type: ignore
    

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn')]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='instagram', null=True, blank=True)
    
    # Verification fields
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(max_length=50, null=True, blank=True)  # 'apify', 'manual', 'screenshot'
    apify_run_id = models.CharField(max_length=100, null=True, blank=True)  # Audit trail

    class Meta:
        unique_together = ('post', 'affiliate', 'platform')
    def __str__(self):
        return f"Like by {self.affiliate.username} on Post {self.post.id}" # type: ignore
    

class Share(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE)
    platform = models.CharField(
        max_length=20,
        choices=[
            ('instagram', 'Instagram'),
            ('linkedin', 'LinkedIn'),
            ('facebook', 'Facebook'),],
        default='instagram',
        null=True,
        blank=True)
        
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Verification fields
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(max_length=50, null=True, blank=True)  # 'apify', 'manual', 'screenshot'
    apify_run_id = models.CharField(max_length=100, null=True, blank=True)  # Audit trail
    
    class Meta:
        unique_together = ('post', 'affiliate', 'platform')
    def __str__(self):
        return f"Share by {self.affiliate.username} on {self.platform}"


# =====================================================
# APIFY SCRAPED DATA MODELS
# =====================================================

class ScrapedPost(models.Model):
    """Tracks which posts have been scraped and when"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='scrapes')
    platform = models.CharField(
        max_length=20,
        choices=[
            ('instagram', 'Instagram'),
            ('facebook', 'Facebook'),
            ('linkedin', 'LinkedIn'),
        ]
    )
    scraped_at = models.DateTimeField(auto_now_add=True)
    total_likes_found = models.IntegerField(default=0)
    total_comments_found = models.IntegerField(default=0)
    apify_run_id = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        unique_together = ('post', 'platform')
        ordering = ['-scraped_at']
    
    def __str__(self):
        return f"{self.post.caption[:30]} - {self.platform} - {self.scraped_at.strftime('%Y-%m-%d')}"


class ScrapedLike(models.Model):
    """Stores all likers found for a post"""
    scraped_post = models.ForeignKey(ScrapedPost, on_delete=models.CASCADE, related_name='likes')
    username = models.CharField(max_length=255)  # Username found on platform
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} - {self.scraped_post}"


class ScrapedComment(models.Model):
    """Stores all commenters found for a post"""
    scraped_post = models.ForeignKey(ScrapedPost, on_delete=models.CASCADE, related_name='comments')
    username = models.CharField(max_length=255)  # Username/name found on platform
    comment_text = models.TextField(null=True, blank=True)  # Optional: store comment text
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} - {self.scraped_post}"


class InstagramComment(models.Model):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="instagram_comments"
    )
    comment_id = models.CharField(max_length=100, unique=True)
    instagram_user_id = models.CharField(max_length=100)
    username = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_id


class PaymentSetting(models.Model):
    PLATFORM_CHOICES = [
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("linkedin", "LinkedIn"),
    ]
    ACTION_CHOICES = [
        ("like", "Like"),
        ("share", "Share"),
        ("comment", "Comment"),
    ]

    super_admin = models.ForeignKey(SuperAdmin, on_delete=models.CASCADE, related_name="payment_settings")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("super_admin", "platform", "action")

    def __str__(self):
        return f"{self.super_admin.name} - {self.platform} {self.action}: {self.amount}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
    ]
    ACTION_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    affiliate = models.ForeignKey(
        AffiliateProfile,
        on_delete=models.CASCADE,
        related_name="withdrawal_requests",
    )
    super_admin = models.ForeignKey(
        SuperAdmin,
        on_delete=models.CASCADE,
        related_name="withdrawal_requests",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.affiliate.username} - Rs {self.amount} ({self.status}, {self.action})"


class AdminNotification(models.Model):
    super_admin = models.ForeignKey(
        SuperAdmin,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    withdrawal_request = models.ForeignKey(
        WithdrawalRequest,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.super_admin.name}: {self.message[:60]}"


def generate_payment_id():
    return f"PAY-{uuid.uuid4().hex[:10].upper()}"


class PaymentHistory(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    affiliate = models.ForeignKey(
        AffiliateProfile,
        on_delete=models.CASCADE,
        related_name="payment_history",
    )
    withdrawal_request = models.OneToOneField(
        WithdrawalRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_history",
    )
    payment_id = models.CharField(max_length=40, unique=True, default=generate_payment_id)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    credits_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    request_date = models.DateTimeField()
    paid_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="paid")
    payment_method = models.CharField(max_length=80, default="Manual Transfer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_date", "-created_at"]

    def __str__(self):
        return f"{self.payment_id} - {self.affiliate.username} - Rs {self.amount_paid}"


class AffiliatePaymentDetail(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("upi", "UPI"),
        ("bank", "Bank Transfer"),
        ("upi_bank", "UPI + Bank Transfer"),
    ]

    affiliate = models.OneToOneField(
        AffiliateProfile,
        on_delete=models.CASCADE,
        related_name="payment_detail",
    )
    preferred_payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="upi",
    )
    upi_id = models.CharField(max_length=120, blank=True, default="")
    account_holder_name = models.CharField(max_length=150, blank=True, default="")
    bank_account_number = models.CharField(max_length=40, blank=True, default="")
    ifsc_code = models.CharField(max_length=20, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.affiliate.username} payment details"
