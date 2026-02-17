from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class SuperAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='super_admin')
    name = models.CharField(max_length=100)
    fbtoken=models.CharField(max_length=300,blank=True, null=True)
    instatoken=models.CharField(max_length=300,blank=True, null=True)
    lntoken=models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
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

    class Meta:
        unique_together = ('post', 'affiliate')
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
    
    class Meta:
        unique_together = ('post', 'affiliate')
    def __str__(self):
        return f"Share by {self.affiliate.username} on {self.platform}"



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
