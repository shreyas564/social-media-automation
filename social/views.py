import requests
import urllib.parse
import re
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect,get_object_or_404
from social.serilizers import AdminSerializer
from social.models import SuperAdmin,Post
from .models import AffiliateProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import models
from .models import Post
from django.contrib.auth.decorators import login_required
from utils.cloudConnect import upload_image_to_cloudinary   
from .models import Like, Post, AffiliateProfile
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import *
from .models import Post, Like, Comment, Share, AffiliateProfile
from utils.cloudConnect import upload_image_to_cloudinary    
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
import json
from .models import AffiliateProfile, Post
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from .models import Post, SuperAdmin, InstagramComment
from utils.facebook import get_insta_user_id


N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"
#sending image

FBTOKEN="EAAJJsrZBrJzwBQnPWHIE5Gooc1jvNlPktigDPWjI0AyUNaLvFWo0ASOX7kUlGTXWqlZAJZBW4OTveRjYskkZC71bs5V1UH4hsZB0dhMvhHdgxfZCS5L1Qz7M2wAWG3ZBgh2Q4kj27Yzk93NHafynoOuHxPSQZA6R6hnKly3JwYIgwDEYj7FxhwIlZAqPPlq3GbEogCMAwkSTjXezAWU5qZBL0ZC2KZAcp3SxiqEdQM2ZAY1sZD"

N8N_Image_Url="http://localhost:5678/webhook-test/image-url"

def send_imageurl(image_url) :
    payload = {
        "image_url": image_url
    }

    try:
        response = requests.post(
            N8N_Image_Url,
            json=payload,
            timeout=60
        )
        print("Payload sent to N8N:", payload)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

    print("N8N Response:", response.text)
    return JsonResponse({
        "success": True,
        "n8n_status": response.status_code,
        "n8n_response": response.text
    })

def send_image_to_n8n(media_url, media_type,caption,post_id,post_name="") :
    
    payload = {
        "media_url": media_url,
        "media_type": media_type,
        "caption": caption,
        "post_name": post_name,
        "post_id": post_id
    }


    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=40
        )
        print("Payload sent to N8N:", payload)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

    print("N8N Response:", response.text)
    return JsonResponse({
        "success": True,
        "n8n_status": response.status_code,
        "n8n_response": response.text
    })

def send_caption_to_n8n(caption):
    payload = {
        "caption": caption
    }

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=40
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

    return JsonResponse({
        "success": True,
        "n8n_status": response.status_code,
        "n8n_response": response.text
    })


def superAdmin(request):
    posts = Post.objects.order_by('-created_at')[:6]
    posts_count = Post.objects.count()
    users = AffiliateProfile.objects.count()

    return render(
        request,
        'superadmin.html',
        {
            'posts': posts,
            'posts_count': posts_count,
            'users': users
        }
    )

#super admin registration

def admin_registration(request):
    return render(request, 'adminregestration.html')

def create_admin(request):
    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(name, email, password)

        serialize_admin = AdminSerializer(data={
            "name": name,
            "email": email,
            "password": password
        }, context=request)

        if serialize_admin.is_valid():
            serialize_admin.save()
        else:
            return JsonResponse({
                "success": False,
                "message": "Invalid data provided"
            }, status=400)

        return redirect('/social/log-admin/')
        
    return JsonResponse({"error": "Invalid method"}, status=405)

def log_admin(request):
    return render(request, 'superadminlogin.html')


def auth_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect('log_admin')

        login(request, user)
        return redirect('super_admin')  

    return JsonResponse({"error": "Invalid method"}, status=405)

import cloudinary.uploader

def upload_media_to_cloudinary(file):

    if file.content_type.startswith("video"):

        result = cloudinary.uploader.upload_large(
            file,
            resource_type="video"
        )

        return result["secure_url"], "video"

    else:

        result = cloudinary.uploader.upload(
            file,
            resource_type="image"
        )

        return result["secure_url"], "image"


def create_post(request):
    return render(request, 'createpost.html')


# def post_submitted(request):
#     print("Post submission received")
#     if request.method == "POST":
#         image = request.FILES.get("post_image")
#         caption = request.POST.get("post_text")
#         post_name = request.POST.get("post_name")
#         user=request.POST.get("user_id") 


#         print("Admin User ID:", user)
#         if not image or not caption:
#             return JsonResponse({
#                 "success": False,
#                 "message": "Image and caption are required"
#             }, status=400)

#         try:
#             super_admin = request.user.super_admin
#         except SuperAdmin.DoesNotExist:
#             return JsonResponse({
#                 "success": False,
#                 "message": "Only SuperAdmins can create posts"
#             }, status=403)


#         image_url = upload_image_to_cloudinary()

        
#         post = Post.objects.create(
#             image=image,   # optional if you want local storage
#             caption=caption,
#             post_name=post_name,
#             created_by=super_admin
#         )
#          # type: ignore
#         post_id = post.id # type: ignore
#         print("Post created with ID:", post_id)
#         print("Image uploaded to Cloudinary:", image_url)
#         send_imageurl(image_url)
#         return send_image_to_n8n(image_url, caption,post.id,post_name) # type: ignore
#     else:
#         JsonResponse({"error": "Invalid method"}, status=405)
def post_submitted(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    media_file = request.FILES.get("post_image")
    caption = request.POST.get("post_text")
    post_name = request.POST.get("post_name")

    if not media_file or not caption:
        return JsonResponse({
            "success": False,
            "message": "Media and caption required"
        }, status=400)

    try:
        super_admin = request.user.super_admin
    except SuperAdmin.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Only SuperAdmins allowed"
        }, status=403)

    # ⭐ Upload to Cloudinary
    media_url, media_type = upload_media_to_cloudinary(media_file)

    # ⭐ Save Post
    post = Post.objects.create(
        media_url=media_url,
        media_type=media_type,
        caption=caption,
        post_name=post_name,
        created_by=super_admin
    )

    # ⭐ Send to N8N
    payload = {
        "media_url": media_url,
        "media_type": media_type,
        "caption": caption,
        "post_id": post.id,
        "post_name": post_name
    }

    try:
        requests.post(N8N_WEBHOOK_URL, json=payload, timeout=40)
    except Exception as e:
        print("N8N ERROR:", e)

    return JsonResponse({"success": True})


#affiliate user regestration


def affiliate_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        instagram_secret = request.POST.get('instagram_secret')
        linkedin_secret = request.POST.get('linkedin_secret')
        facebook_secret = request.POST.get('facebook_secret')
        twitter_secret = request.POST.get('twitter_secret')

        if AffiliateProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('affiliate_register')

        AffiliateProfile.objects.create(
            username=username,
            password=make_password(password),  # hash password
            instagram_secret=make_password(instagram_secret),
            linkedin_secret=make_password(linkedin_secret),
            facebook_secret=make_password(facebook_secret),
            twitter_secret=make_password(twitter_secret),
        )

        messages.success(request, "Affiliate registered successfully")
        return redirect('affiliate_login')

    return render(request, 'regestration.html')

#Affiliated user Login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import AffiliateProfile


def affiliate_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            affiliate = AffiliateProfile.objects.get(username=username)
        except AffiliateProfile.DoesNotExist:
            messages.error(request, "Invalid username or password")
            return redirect('affiliate_login')

        if check_password(password, affiliate.password):
            request.session['affiliate_id'] = affiliate.id # type: ignore
            request.session['affiliate_username'] = affiliate.username
            return redirect('affiliate_dashboard')  # REDIRECT HERE
        else:
            messages.error(request, "Invalid username or password")
            return redirect('affiliate_login')

    return render(request, 'affiliateduserlogin.html')


# Affiliated user dashboard
def affiliate_dashboard(request):
    if not request.session.get('affiliate_id'):
        return redirect('affiliate_login')

    posts = Post.objects.all().order_by('-created_at')

    return render(
        request,
        'affiliate_userdashboard.html',
        {'posts': posts}
    )

def like_post(request):
    affiliate_id = request.session.get("affiliate_id")
    post_id = request.POST.get("post_id")
    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)
    Like.objects.get_or_create(affiliate = affiliate,post=post)
    return JsonResponse({"status":"success"})

def comment_post(request):
    affiliate_id = request.session.get("affiliate_id")
    post_id = request.POST.get("post_id")
    comment_text = request.POST.get("comment_text")
    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)
    Comment.objects.create(affiliate = affiliate,post=post,text=comment_text)
    return JsonResponse({"status":"success"})

def share_post(request):
    affiliate_id = request.session.get("affiliate_id")
    post_id = request.POST.get("post_id")
    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)
    Share.objects.create(affiliate = affiliate,post=post)
    return JsonResponse({"status":"success"})


#for affiliate regestration side
# @require_POST
# def affiliate_like_post(request):
#     affiliate_id = request.session.get("affiliate_id")

#     if not affiliate_id:
#         return JsonResponse(
#             {"error": "Affiliate not logged in"},
#             status=403
#         )

#     post_id = request.POST.get("post_id")

#     if not post_id:
#         return JsonResponse(
#             {"error": "Post ID missing"},
#             status=400
#         )

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
#     post = get_object_or_404(Post, id=post_id)

#     like, created = Like.objects.get_or_create(
#         affiliate=affiliate,
#         post=post
#     )

#     if not created:
#         return JsonResponse({
#             "status": "already_liked",
#             "message": "You already liked this post"
#         })

#     return JsonResponse({
#         "status": "success",
#         "message": "Post liked successfully"
#     })



# # COMMENT POST
# @require_POST
# def affiliate_comment_post(request):
#     affiliate_id = request.session.get("affiliate_id")

#     if not affiliate_id:
#         return JsonResponse(
#             {"error": "Affiliate not logged in"},
#             status=403
#         )

#     post_id = request.POST.get("post_id")
#     comment_text = request.POST.get("comment_text")

#     if not post_id or not comment_text:
#         return JsonResponse(
#             {"error": "Post ID or comment missing"},
#             status=400
#         )

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
#     post = get_object_or_404(Post, id=post_id)

#     Comment.objects.create(
#         affiliate=affiliate,
#         post=post,
#         text=comment_text
#     )

#     return JsonResponse({
#         "status": "success",
#         "message": "Comment added successfully"
#     })


# # SHARE POST
# @require_POST
# def affiliate_share_post(request):
#     affiliate_id = request.session.get("affiliate_id")

#     if not affiliate_id:
#         return JsonResponse(
#             {"error": "Affiliate not logged in"},
#             status=403
#         )

#     post_id = request.POST.get("post_id")
#     platform = request.POST.get("platform")

#     if not post_id or not platform:
#         return JsonResponse(
#             {"error": "Post ID or platform missing"},
#             status=400
#         )

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
#     post = get_object_or_404(Post, id=post_id)

#     Share.objects.create(
#         affiliate=affiliate,
#         post=post,
#         platform=platform
#     )

#     return JsonResponse({
#         "status": "success",
#         "message": "Post shared successfully"
#     })

#  AFFILIATE SETTINGS PAGE
def usersettings(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'affiliatesettings.html', {'affiliate': affiliate})



#UPDATE AFFILIATE PROFILE (POST)
@require_POST
def update_affiliate_profile(request):
    affiliate_id = request.session.get('affiliate_id')

    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)

    affiliate.username = request.POST.get("username", affiliate.username)
    
    # Update platform usernames for verification
    affiliate.instagram_username = request.POST.get("instagram_username", affiliate.instagram_username)
    affiliate.facebook_username = request.POST.get("facebook_username", affiliate.facebook_username)
    affiliate.linkedin_username = request.POST.get("linkedin_username", affiliate.linkedin_username)

    if request.POST.get("instagram_secret"):
        affiliate.instagram_secret = make_password(
            request.POST.get("instagram_secret")
        )

    if request.POST.get("facebook_secret"):
        affiliate.facebook_secret = make_password(
            request.POST.get("facebook_secret")
        )

    if request.POST.get("linkedin_secret"):
        affiliate.linkedin_secret = make_password(
            request.POST.get("linkedin_secret")
        )

    if request.POST.get("twitter_secret"):
        affiliate.twitter_secret = make_password(
            request.POST.get("twitter_secret")
        )

    affiliate.save()

    messages.success(request, "Profile updated successfully")
    return redirect('usersettings')

# CHANGE  AFFILIATE USER PASSWORD (POST)
@require_POST
def change_affiliate_password(request):
    affiliate = get_object_or_404(
        AffiliateProfile,
        id=request.session.get('affiliate_id')
    )

    if not check_password(request.POST.get('old_password'), affiliate.password):
        messages.error(request, "Old password is incorrect")
        return redirect('affiliate_profile')

    if request.POST.get('new_password') != request.POST.get('confirm_password'):
        messages.error(request, "Passwords do not match")
        return redirect('affiliate_profile')

    affiliate.password = make_password(request.POST.get('new_password'))
    affiliate.save()

    messages.success(request, "Password changed successfully")
    return redirect('usersettings')

# LOGOUT
def affiliate_logout(request):
    request.session.flush()
    return redirect('affiliate_login')


#SUPER ADMIN SIDE 
def posts_list(request):
    posts = Post.objects.all().order_by('-created_at').prefetch_related('scrapes')
    
    # Organize scraped data for easy access in template
    for post in posts:
        post.scraped_info = {s.platform: s for s in post.scrapes.all()}
        
    return render(request, 'postslist.html', {'posts': posts})



# =========================
# AFFILIATE FEED
# =========================
def affiliate_feed(request):
    if not request.session.get('affiliate_id'):
        return redirect('affiliate_login')

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'affiliate_userdashboard.html', {'posts': posts})


# =========================
# SETTINGS PAGE
# =========================
def afflilate_settings(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'settings.html', {'affiliate': affiliate})


# =========================
# AFFILIATE PROFILE PAGE
# =========================
def affiliate_profile(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'affiliate_profile.html', {'affiliate': affiliate})



def edit_affiliate_profile(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'edit_affiliate_profile.html', {'affiliate': affiliate})


def change_password_page(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    return render(request, 'change_password.html')


def affiliate_users(request):
    from django.db.models import Count, Q
    from datetime import timedelta
    from django.utils import timezone
    # Ensure these are imported or available
    from .models import ScrapedLike, ScrapedComment

    affiliate_profiles = AffiliateProfile.objects.all()

    # Build statistics for each affiliate
    stats_data = []

    for affiliate in affiliate_profiles:
        # 1. Total claimed engagement (from manual button clicks)
        total_likes = Like.objects.filter(affiliate=affiliate).count()
        total_comments = Comment.objects.filter(affiliate=affiliate).count()
        total_shares = Share.objects.filter(affiliate=affiliate).count()
        
        # 2. Scraped/Found engagement (Direct database check)
        scraped_likes_count = 0
        scraped_comments_count = 0
        
        # Instagram
        if affiliate.instagram_username:
            scraped_likes_count += ScrapedLike.objects.filter(
                scraped_post__platform='instagram', 
                username__iexact=affiliate.instagram_username
            ).count()
            scraped_comments_count += ScrapedComment.objects.filter(
                scraped_post__platform='instagram', 
                username__iexact=affiliate.instagram_username
            ).count()
            
        # Facebook
        if affiliate.facebook_username:
            scraped_likes_count += ScrapedLike.objects.filter(
                scraped_post__platform='facebook', 
                username__iexact=affiliate.facebook_username
            ).count()
            scraped_comments_count += ScrapedComment.objects.filter(
                scraped_post__platform='facebook', 
                username__iexact=affiliate.facebook_username
            ).count()
            
        # LinkedIn
        if affiliate.linkedin_username:
            scraped_likes_count += ScrapedLike.objects.filter(
                scraped_post__platform='linkedin', 
                username__iexact=affiliate.linkedin_username
            ).count()
            scraped_comments_count += ScrapedComment.objects.filter(
                scraped_post__platform='linkedin', 
                username__iexact=affiliate.linkedin_username
            ).count()

        # Structure data for this affiliate
        affiliate_stats = {
            'affiliate': affiliate,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'total_engagement': total_likes + total_comments + total_shares,
            # Use these new fields in template
            'scraped_likes': scraped_likes_count,
            'scraped_comments': scraped_comments_count,
            'credits': 0,  # Placeholder for future logic
        }

        stats_data.append(affiliate_stats)
    
    context = {
        'users_stats': stats_data,
        # Removed pending/verified overview stats as requested
    }

    return render(request, 'affiliateusers.html', context)


def verification_dashboard(request):
    """Dashboard showing pending verifications and stats"""
    from datetime import timedelta
    from django.utils import timezone
    
    # Get pending verifications (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    
    pending_likes = Like.objects.filter(
        is_verified=False,
        created_at__gte=week_ago
    ).select_related('post', 'affiliate').order_by('-created_at')[:50]
    
    pending_comments = Comment.objects.filter(
        is_verified=False,
        created_at__gte=week_ago
    ).select_related('post', 'affiliate').order_by('-created_at')[:50]
    
    # Get verification stats
    total_likes = Like.objects.filter(created_at__gte=week_ago).count()
    total_comments = Comment.objects.filter(created_at__gte=week_ago).count()
    
    verified_likes = Like.objects.filter(created_at__gte=week_ago, is_verified=True).count()
    verified_comments = Comment.objects.filter(created_at__gte=week_ago, is_verified=True).count()
    
    context = {
        'pending_likes': pending_likes,
        'pending_comments': pending_comments,
        'pending_count': pending_likes.count() + pending_comments.count(),
        'verified_likes': verified_likes,
        'verified_comments': verified_comments,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'verification_rate': round((verified_likes + verified_comments) / max(total_likes + total_comments, 1) * 100, 1)
    }
    
    return render(request, 'verification_dashboard.html', context)


def trigger_verification(request):
    """Trigger Apify verification for recent engagement"""
    from django.contrib import messages
    from utils.verification_service import VerificationService
    import os
    
    if request.method == 'POST':
        # Check if Apify token is configured
        if not os.getenv('APIFY_TOKEN'):
            messages.error(request, '❌ Apify token not configured. Please add APIFY_TOKEN to .env file.')
            return redirect('affiliate_users')
        
        try:
            service = VerificationService()
            
            # Run verification
            results = service.verify_all_recent_engagement(days=7, limit=50)
            
            # Show success message with stats
            verified_total = results['verified_likes'] + results['verified_comments']
            checked_total = results['total_likes_checked'] + results['total_comments_checked']
            
            messages.success(
                request, 
                f'✓ Verification complete! Verified {verified_total}/{checked_total} items. '
                f'({results["verified_likes"]} likes, {results["verified_comments"]} comments)'
            )
        
        except Exception as e:
            messages.error(request, f'❌ Verification error: {str(e)}')
    
    return redirect('affiliate_users')


def scrape_post_data(request, post_id):
    """Scrape a post and save all engagement data to database"""
    from django.contrib import messages
    from utils.post_scraper import PostScrapingService
    import os
    
    if request.method == 'POST':
        platform = request.POST.get('platform')
        
        if not os.getenv('APIFY_TOKEN'):
            messages.error(request, '❌ Apify token not configured')
            return redirect('post_stats')
        
        try:
            service = PostScrapingService()
            from utils.post_verification import PostVerificationService
            verify_service = PostVerificationService()
            
            platforms_to_scrape = []
            if platform == 'all':
                post = Post.objects.get(id=post_id)
                if post.Ipost_url: platforms_to_scrape.append('instagram')
                if post.Fposturl: platforms_to_scrape.append('facebook')
                if post.Lposturl: platforms_to_scrape.append('linkedin')
            else:
                platforms_to_scrape = [platform]
            
            results = []
            for p in platforms_to_scrape:
                result = service.scrape_post(post_id, p)
                if result['success']:
                    verify_result = verify_service.verify_post_engagement(post_id, p)
                    results.append(f"✓ {p.title()}: {result['likes_found']}L/{verify_result.get('verified_likes', 0)} verified")
                else:
                    results.append(f"❌ {p.title()}: {result.get('error')}")
            
            if results:
                messages.success(request, " | ".join(results))
            else:
                messages.warning(request, "No platforms available to scrape")
        
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
    
    return redirect('post_stats')


def verify_post_data(request, post_id):
    """Verify affiliates against scraped data in database"""
    from django.contrib import messages
    from utils.post_verification import PostVerificationService
    
    if request.method == 'POST':
        platform = request.POST.get('platform')
        
        try:
            service = PostVerificationService()
            result = service.verify_post_engagement(post_id, platform)
            
            if result['success']:
                messages.success(
                    request,
                    f"✓ Verified {platform.title()}: {result['verified_likes']} likes, "
                    f"{result['verified_comments']} comments matched"
                )
            else:
                messages.error(request, f"❌ {result.get('error', 'Verification failed')}")
        
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
    
    return redirect('posts_list')


def setting(request):
    return render(request, 'settings.html')

def profile(request):
    return render(request, 'profile.html')

def update_admin_profile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        global FBTOKEN
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        super_admin=SuperAdmin.objects.get(id=user.id)

        super_admin.fbtoken=request.POST.get("fbtoken")
        super_admin.instatoken=request.POST.get("instatoken")
        super_admin.lntoken=request.POST.get("lntoken")
        super_admin.save()

        FBTOKEN=super_admin.fbtoken
        print(FBTOKEN)
        print(user)

        messages.success(request, "Profile updated successfully")
        return render(request, 'profile.html', {'super_admin': super_admin})

    return JsonResponse({"error": "Invalid method"}, status=405)

def change_password(request):
    return render(request, 'changepassword.html')

def update_password(request):
    if request.method == "POST":
        current_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password1")
        confirm_password = request.POST.get("new_password2")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect('change_password')

        user.set_password(new_password)
        user.save()


        messages.success(request, "Password updated successfully")
        return render(request, 'profile.html')

    return JsonResponse({"error": "Invalid method"}, status=405)

def editpost(request,post_id):
    post=Post.objects.get(id=post_id)
    return render(request, 'editpost.html', {'post': post})
def edit_facebook_post(post_id, access_token, new_caption):
    
    if not post_id:
        return True

    url = f"https://graph.facebook.com/v19.0/{post_id}"

    payload = {
        "message": new_caption,
        "access_token": access_token.strip()
    }

    res = requests.post(url, data=payload)

    print("FB EDIT:", res.status_code, res.text)

    return res.status_code == 200

def submit_editpost(request, post_id):
    
    if request.method == "POST":

        caption = request.POST.get("caption")

        post = Post.objects.get(id=post_id)
        super_admin = SuperAdmin.objects.get(user=request.user)

        # -------- Update DB --------
        post.caption = caption
        post.save()

        # -------- FACEBOOK EDIT --------
        if post.fbpostid and super_admin.fbtoken:
            edit_facebook_post(
                post.fbpostid,
                super_admin.fbtoken,
                caption
            )

        # -------- N8N --------
        send_caption_to_n8n(caption)

        return redirect('posts_list')

    

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


@login_required
def del_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    super_admin = get_object_or_404(SuperAdmin, user=request.user)

    fb_ok = True
    ig_ok = True
    ln_ok = True

    # FACEBOOK
    if post.fbpostid and super_admin.fbtoken:
        fb_ok = delete_facebook_post(post.fbpostid, super_admin.fbtoken)

    # INSTAGRAM ✅ FIX ADDED
    if post.instapostid and super_admin.instatoken:
        ig_ok = delete_instagram_post(post.instapostid, super_admin.instatoken)

    # LINKEDIN
    if post.lnpostid and super_admin.lntoken:
        ln_ok = delete_linkedin_post(post.lnpostid, super_admin.lntoken)

    post.delete()

    if fb_ok and ig_ok and ln_ok:
        messages.success(request, "Deleted from dashboard & all platforms")
    else:
        messages.warning(request, "Deleted locally but failed on some platforms")

    return redirect("posts_list")




    
def logout_view(request):
    logout(request)
    return redirect('log_admin')


@csrf_exempt
def collect_post_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    payload = json.loads(request.body)
    posts = payload.get("posts", [])
    caption = payload.get("caption")

    updated = set()

    for item in posts:
        post_id = item.get("postid")
        platform = item.get("platform")
        post_url = item.get("post_url")  # ✅ CORRECT KEY

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            continue

        # update caption once
        if caption and post.id not in updated:
            post.caption = caption
            updated.add(post.id)

        if platform == "facebook":
            post.fbpostid = item.get("post_id")
            post.Fposturl = post_url

        elif platform == "instagram":
            post.instapostid = item.get("post_id")
            post.Ipost_url = post_url

        elif platform == "linkedin":
            post.lnpostid = item.get("post_id")
            post.Lposturl = post_url

        post.save()

    return JsonResponse({
        "status": "success",
        "updated_posts": list(updated)
    })

def delete_facebook_post(post_id, access_token):
    if not post_id:
        return True

    url = f"https://graph.facebook.com/v19.0/{post_id}"
    res = requests.delete(url, params={"access_token": access_token})

    print("FB STATUS:", res.status_code, res.text)
    return res.status_code in [200, 204]

def delete_instagram_post(media_id, access_token):
    if not media_id:
        return True

    url = f"https://graph.facebook.com/v19.0/{media_id}"
    res = requests.delete(url, params={"access_token": access_token})

    print("IG STATUS:", res.status_code, res.text)
    return res.status_code in [200, 204]

def delete_linkedin_post(post_urn, access_token):
    if not post_urn:
        return True

    if not post_urn.startswith("urn:li:"):
        post_urn = f"urn:li:ugcPost:{post_urn}"

    encoded_urn = urllib.parse.quote(post_urn, safe="")

    url = f"https://api.linkedin.com/v2/ugcPosts/{encoded_urn}"
    headers = {
        "Authorization": f"Bearer {access_token.strip()}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    res = requests.delete(url, headers=headers)

    print("LN STATUS:", res.status_code, res.text)
    return res.status_code == 204

@login_required
def postStat(request):

    admin = SuperAdmin.objects.get(user=request.user)
    posts = Post.objects.filter(created_by=admin).order_by("-created_at").prefetch_related(
        'scrapes__likes', 
        'scrapes__comments'
    )

    # Organize scraped data for easy access in template
    for post in posts:
        post.scraped_info = {s.platform: s for s in post.scrapes.all()}

    return render(request, "postStat.html", {"posts": posts})


def _sync_post_stats_for_admin(admin):
    """
    Sync post stats from ScrapedPost data instead of live API calls.
    This ensures we use the data we paid for via Apify.
    """
    posts = list(Post.objects.filter(created_by=admin).prefetch_related('scrapes'))
    if not posts:
        return 0, 0

    dirty_posts = []
    update_fields = [
        "ig_likes", "ig_comments",
        "fb_likes", "fb_comments",
        "li_likes", "li_comments",
    ]

    for post in posts:
        changed = False
        
        # Get scraped data map
        scrapes = {s.platform: s for s in post.scrapes.all()}
        
        # Update Instagram
        if 'instagram' in scrapes:
            s = scrapes['instagram']
            if post.ig_likes != s.total_likes_found or post.ig_comments != s.total_comments_found:
                post.ig_likes = s.total_likes_found
                post.ig_comments = s.total_comments_found
                changed = True
        
        # Update Facebook
        if 'facebook' in scrapes:
            s = scrapes['facebook']
            if post.fb_likes != s.total_likes_found or post.fb_comments != s.total_comments_found:
                post.fb_likes = s.total_likes_found
                post.fb_comments = s.total_comments_found
                changed = True
                
        # Update LinkedIn
        if 'linkedin' in scrapes:
            s = scrapes['linkedin']
            if post.li_likes != s.total_likes_found or post.li_comments != s.total_comments_found:
                post.li_likes = s.total_likes_found
                post.li_comments = s.total_comments_found
                changed = True

        if changed:
            dirty_posts.append(post)

    if dirty_posts:
        Post.objects.bulk_update(dirty_posts, update_fields)

    return len(dirty_posts), len(posts)


def _sync_single_post_stats_for_admin(admin, post):
    changed = False

    if post.instapostid and admin.instatoken:
        ig = get_instagram_stats(post.instapostid, admin.instatoken)
        ig_likes = ig.get("likes", 0)
        ig_comments = ig.get("comments", 0)
        ig_shares = ig.get("shares", "NA")
        if (
            post.ig_likes != ig_likes
            or post.ig_comments != ig_comments
            or post.ig_shares != ig_shares
        ):
            post.ig_likes = ig_likes
            post.ig_comments = ig_comments
            post.ig_shares = ig_shares
            changed = True

    fb_target = post.fbpostid or post.Fposturl
    if fb_target and admin.fbtoken:
        fb = get_facebook_stats(fb_target, admin.fbtoken)
        fb_likes = fb.get("likes", 0)
        fb_comments = fb.get("comments", 0)
        fb_shares = fb.get("shares", 0)
        if (
            post.fb_likes != fb_likes
            or post.fb_comments != fb_comments
            or post.fb_shares != fb_shares
        ):
            post.fb_likes = fb_likes
            post.fb_comments = fb_comments
            post.fb_shares = fb_shares
            changed = True

    if post.lnpostid and admin.lntoken:
        li = get_linkedin_stats(post.lnpostid, admin.lntoken)
        li_likes = li.get("likes", 0)
        li_comments = li.get("comments", 0)
        li_shares = li.get("shares", 0)
        if (
            post.li_likes != li_likes
            or post.li_comments != li_comments
            or post.li_shares != li_shares
        ):
            post.li_likes = li_likes
            post.li_comments = li_comments
            post.li_shares = li_shares
            changed = True

    if changed:
        post.save(
            update_fields=[
                "ig_likes", "ig_comments", "ig_shares",
                "fb_likes", "fb_comments", "fb_shares",
                "li_likes", "li_comments", "li_shares",
            ]
        )

    return changed


@login_required
@require_POST
def sync_post_stats(request):
    admin = SuperAdmin.objects.get(user=request.user)
    updated_count, total_count = _sync_post_stats_for_admin(admin)
    messages.success(
        request,
        f"Stats synced. Updated {updated_count} of {total_count} posts."
    )
    return redirect("post_stats")


@login_required
@require_POST
def sync_single_post_stats(request, post_id):
    admin = SuperAdmin.objects.get(user=request.user)
    post = get_object_or_404(Post, id=post_id, created_by=admin)
    changed = _sync_single_post_stats_for_admin(admin, post)
    if changed:
        messages.success(request, f"Stats synced for '{post.post_name}'.")
    else:
        messages.info(request, f"No changes for '{post.post_name}'.")
    return redirect("post_stats")

    

def get_insta_likes_and_comments(request, ipostid, token):
    url = f"https://graph.facebook.com/v19.0/{ipostid}"
    params = {
        "fields": "like_count,comments_count",
        "access_token": token
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return JsonResponse({
            "post_id": ipostid,
            "like_count": data.get("like_count", 0),
            "comments_count": data.get("comments_count", 0)
        })

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"error": str(e)},
            status=400
        )


    return JsonResponse(
        {"error": "Unexpected server error"},
        status=500
    )



def add_page(request):
    if request.method == 'POST':
        pageName=request.POST.get('pageName')
        pageId=request.POST.get('pageId')

       
        page=Pages.objects.create(
            pageId=pageId,
            pageName=pageName  
            )
        
        print("Page created")

    pages=Pages.objects.all()
    
    return render(request,"pages.html",{"pages":pages})


def add_fb_page(request):
    return render(request, "fbpages.html")


FB_BASE_URL = "https://graph.facebook.com/v19.0"
FB_ACCESS_TOKEN = "EAAMcHkCZAkvIBQmgeWZAOZAtYLn0kNdjGlkefFmYf5T5WNE9z3vMK3oCDQ6thSYxvPXJ6qjCTYsbaFjGXO28RLRbqn5aDqonTqV9UEF3O28trT2LhobR9AUcObfl0IZC8dLo9d8QnJnwVjnJ0n69qqnD1BGAL3qnkAFy2a9dnpfyCHaM1lEcgIeJF2erd2cHJ4LYnPzJ4ffuSUaFPvVlu0lcC04zHycSXK7kzSEZD"


# def post_stats_view(request):
#     posts = Post.objects.all()   

#     print("POST COUNT:", posts.count())  

#     return render(
#         request,
#         "social/postStat.html",
#         {"posts": posts}
#     )
# def post_stats_view(request):
    
#     admin = SuperAdmin.objects.get(user=request.user)
#     posts = Post.objects.filter(created_by=admin)

#     for post in posts:

#         # INSTAGRAM
#         insta_stats = fetch_instagram_stats(post.instapostid, admin.instatoken)

#         # FACEBOOK
#         fb_stats = fetch_facebook_stats(post.fbpostid, admin.fbtoken)

#         # LINKEDIN
#         ln_stats = fetch_linkedin_stats(post.lnpostid, admin.lntoken)

#         # Save into model
#         post.insta_likes = insta_stats["likes"]
#         post.insta_comments = insta_stats["comments"]

#         post.fb_likes = fb_stats["likes"]
#         post.fb_comments = fb_stats["comments"]
#         post.fb_shares = fb_stats["shares"]

#         post.ln_likes = ln_stats["likes"]
#         post.ln_comments = ln_stats["comments"]
#         post.ln_shares = ln_stats["shares"]

#     return render(request, "post_stats.html", {"posts": posts})


# ---------------- FACEBOOK ----------------
def _extract_fb_object_ids(raw_value):
    """
    Return likely Facebook object IDs from a raw ID or Facebook URL.
    """
    if not raw_value:
        return []

    value = str(raw_value).strip()
    candidates = [value]

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urllib.parse.urlparse(value)
        query = urllib.parse.parse_qs(parsed.query)
        path = parsed.path or ""

        for key in ("story_fbid", "fbid", "v"):
            q_val = query.get(key, [None])[0]
            if q_val:
                candidates.append(q_val)

        path_match = re.search(r"/(?:posts|videos|reel|watch)/([0-9_]+)", path)
        if path_match:
            candidates.append(path_match.group(1))

        trailing_match = re.search(r"/([0-9_]{6,})/?$", path)
        if trailing_match:
            candidates.append(trailing_match.group(1))

    deduped = []
    seen = set()
    for item in candidates:
        if item and item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _fb_total_count(data, primary_key, fallback_key=None):
    primary = data.get(primary_key, {}).get("summary", {}).get("total_count", 0)
    if primary:
        return primary
    if fallback_key:
        return data.get(fallback_key, {}).get("summary", {}).get("total_count", 0)
    return 0


def get_facebook_stats(post_id, access_token):
    token = (access_token or "").strip()
    if not post_id or not token:
        return {"likes": 0, "comments": 0, "shares": 0}

    stats_fields = "reactions.summary(true),likes.summary(true),comments.summary(true),shares"

    for object_id in _extract_fb_object_ids(post_id):
        base_url = f"{FB_BASE_URL}/{object_id}"
        params = {
            "fields": stats_fields,
            "access_token": token,
        }

        try:
            res = requests.get(base_url, params=params, timeout=15).json()
        except requests.RequestException:
            continue

        if "error" in res:
            error_msg = str(res.get("error", {}).get("message", ""))
            print(f"FB STATS ERROR ({object_id}):", res.get("error"))

            # Reels/video objects may not expose "reactions"; retry with video-safe fields.
            if "node type (Video)" in error_msg and "reactions" in error_msg:
                video_params = {
                    "fields": "likes.summary(true),comments.summary(true)",
                    "access_token": token,
                }
                try:
                    video_res = requests.get(base_url, params=video_params, timeout=15).json()
                    if "error" not in video_res:
                        likes = video_res.get("likes", {}).get("summary", {}).get("total_count", 0)
                        comments = video_res.get("comments", {}).get("summary", {}).get("total_count", 0)
                        shares = 0
                        return {"likes": likes, "comments": comments, "shares": shares}
                except requests.RequestException:
                    pass
            continue

        likes = _fb_total_count(res, "reactions", fallback_key="likes")
        comments = res.get("comments", {}).get("summary", {}).get("total_count", 0)
        shares = res.get("shares", {}).get("count", 0)

        # Video stats can live on attached video object instead of the post object.
        # Request attachments only when needed to avoid compatibility errors.
        if likes == 0 and comments == 0:
            attachment_params = {
                "fields": "attachments{media_type,target{id}}",
                "access_token": token,
            }
            try:
                attachment_res = requests.get(
                    base_url,
                    params=attachment_params,
                    timeout=15
                ).json()
            except requests.RequestException:
                attachment_res = {}

            attachment = attachment_res.get("attachments", {}).get("data", [{}])[0]
            media_type = attachment.get("media_type", "")
            video_id = attachment.get("target", {}).get("id")

            if media_type and "video" in media_type.lower() and video_id:
                video_params = {
                    "fields": stats_fields,
                    "access_token": token,
                }
                try:
                    video_res = requests.get(
                        f"{FB_BASE_URL}/{video_id}",
                        params=video_params,
                        timeout=15
                    ).json()
                    if "error" not in video_res:
                        likes = _fb_total_count(video_res, "reactions", fallback_key="likes")
                        comments = video_res.get("comments", {}).get("summary", {}).get("total_count", 0)
                        shares = video_res.get("shares", {}).get("count", shares)
                except requests.RequestException:
                    pass

        print(
            f"FB STATS ({object_id}) likes={likes} comments={comments} shares={shares}"
        )
        return {"likes": likes, "comments": comments, "shares": shares}

    return {"likes": 0, "comments": 0, "shares": 0}


# ---------------- INSTAGRAM ----------------
def get_instagram_stats(media_id,access_token):
    # Instagram Graph API
    url = f"{FB_BASE_URL}/{media_id}"
    params = {
        "fields": "like_count,comments_count",
        "access_token": access_token.strip()
    }

    res = requests.get(url, params=params).json()

    return {
        "likes": res.get("like_count", 0),
        "comments": res.get("comments_count", 0),
        "shares":"NA" #Instagram does not provide share count
    }



# ---------------- LINKEDIN ----------------
def get_linkedin_stats(post_urn, access_token):
    if not post_urn or not access_token:
        return {"likes": 0, "comments": 0, "shares": 0}

    urn = post_urn.strip()
    if not urn.startswith("urn:li:"):
        if urn.isdigit():
            urn = f"urn:li:ugcPost:{urn}"
        else:
            return {"likes": 0, "comments": 0, "shares": 0}

    encoded_urn = urllib.parse.quote(urn, safe="")
    url = f"https://api.linkedin.com/rest/socialActions/{encoded_urn}"
    headers = {
        "Authorization": f"Bearer {access_token.strip()}",
        "Linkedin-Version": "202503",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
    except requests.RequestException:
        return {"likes": 0, "comments": 0, "shares": 0}

    if res.status_code != 200 or "status" in data:
        print("LinkedIn stats error:", res.status_code, data)
        return {"likes": 0, "comments": 0, "shares": 0}

    return {
        "likes": data.get("likesSummary", {}).get("totalLikes", 0),
        "comments": (
            data.get("commentsSummary", {}).get("totalFirstLevelComments", 0)
            or data.get("commentsSummary", {}).get("totalComments", 0)
        ),
        "shares": data.get("sharesSummary", {}).get("totalShares", 0),
    }


# ---------------- AJAX HANDLER ----------------
# views.py
from django.http import JsonResponse
from utils.facebook import (
    get_facebook_likes_count,
    get_facebook_comments_count,
    get_share_count
)


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from dateutil.parser import parse
from django.db import IntegrityError

@login_required
def sync_instagram_comments(request):
    ACCESS_TOKEN = "EAAREJYWQqckBQsYZAZAJO1H2vPwJqn7gBahJPiIRMsgtTl5ifqEcTXvCjZCiOeHASClZBEaXPkwDMTUkzeqPfvXMjdAZCBZAjiZCWTnZArL9snKuVd7lqb6OKuO4oZAmjZCK6aijL0h18HAZCPOKnMe0hghA2M6SYUlwG2ZB4mQ8dBZChZAKGB1J1zDeHgYKntbvit"

    super_admin = SuperAdmin.objects.get(user=request.user)

    posts = Post.objects.filter(
        created_by=super_admin,
        instapostid__isnull=False
    ).exclude(instapostid="")

    inserted = 0
    skipped = 0

    for post in posts:
        url = f"https://graph.facebook.com/v19.0/{post.instapostid}/comments"
        params = {
            "fields": "id,text,timestamp,from{id,username}",
            "access_token": ACCESS_TOKEN
        }

        response = requests.get(url, params=params)

        
        print("POST:", post.id, post.instapostid)
        print("API RESPONSE:", response.json())

        if response.status_code != 200:
            continue

        for comment in response.json().get("data", []):

            from_data = comment.get("from")
            if not from_data:
                continue

            try:
                obj, created = InstagramComment.objects.get_or_create(
                    comment_id=comment["id"],
                    defaults={
                        "post": post,
                        "instagram_user_id": from_data.get("id"),
                        "username": from_data.get("username"),
                        "text": comment.get("text"),
                        "timestamp": parse(comment.get("timestamp")),
                    }
                )

                if created:
                    inserted += 1
                else:
                    skipped += 1

            except IntegrityError as e:
                skipped += 1
                print("DB ERROR:", e)

            except Exception as e:
                print("UNEXPECTED ERROR:", e)

    return JsonResponse({
        "status": "success",
        "inserted_rows": inserted,
        "skipped_rows": skipped
    })



def get_facebook_commenters(request, postid):


    ACCESS_TOKEN = "EAAMcHkCZAkvIBQizcNQy6srhlnCNTjkghxjTSylFREOzeCoNFpyFDWO7ZA8wZCzm1cIINl919eM9o1oUbyaCwbiwE1ZC6r90wgjZA5xHlpGFEQh5LG8Gw5dvEnQqRmGXg6Fl6EmKbtL8QMqmb4jLZBcZBeZBepThlJ0iRPZCWjiAg0oMH10J8uOkJO1Jrf6jev2URpRI0bZBOh7n01rk4w7UyT4PzUlfmmS6fcGtTKI9q8V25ZA"

    if not ACCESS_TOKEN:
        return JsonResponse(
            {"error": "Facebook Page access token is missing"},
            status=400
        )

    url = f"https://graph.facebook.com/v19.0/{postid}/comments"
 
    params = {
        "fields": "from{id,name},created_time",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return JsonResponse(response.json(), status=response.status_code)

    commenters = []
    for comment in response.json().get("data", []):
        user = comment.get("from", {})
        commenters.append({
            "user_id": user.get("id"),
            "name": user.get("name"),
            "commented_at": comment.get("created_time")
        })

    return JsonResponse({
        "total_comments": len(commenters),
        "commenters": commenters
    })



ACCESS_TOKEN = "AQXSC5K8LvpiOiW0FvvzuoJnHTOyC2lraSeH22XA9FqquQu6oBv1wxOgdJUxrsKAXglGfeHzSpS1QnjUgxU1VR63ZtXplpovW8Ebd0JraMrrItgrOYM7BZgMO0E_lIRGC4QCalVzLen8jof2IW8_5U7svcGzIGWT1TPeJsbLVT4fRvOj5Aw8B1RrWtdzA4FX68edqYhdZPpSDVFkGYG-Lvi7yPWpP8dRnGvyBQqjQLp607rKr-JGvhMjCT04MNLldU0J7mVD_bRFvA-QgC-B7Arh6s5BKxDxwAAndv8sXsJiaVkEQSHRqmR5ELxV2zWJs71s0rsGoiVZ3zySRNretPegIozvCg"
def get_linkedin_comments(request, ugc_post_urn):
    access_token = request.headers.get("Authorization")

    if not access_token:
        return JsonResponse(
            {"error": "Authorization header missing"},
            status=401
        )

    if not access_token.startswith("Bearer "):
        access_token = f"Bearer {access_token}"

    url = "https://api.linkedin.com/v2/socialActions/{}/comments".format(
        ugc_post_urn
    )

    headers = {
        "Authorization": access_token,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    params = {
        "q": "socialAction",
        "count": 50
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return JsonResponse(
            {
                "error": "LinkedIn API error",
                "status": response.status_code,
                "details": response.text
            },
            status=response.status_code
        )

    data = response.json()

    comments = []

    for element in data.get("elements", []):
        comments.append({
            "comment_id": element.get("id"),
            "actor_urn": element.get("actor"),
            "message": element.get("message", {}).get("text"),
            "created_time": element.get("created", {}).get("time"),
            "parent_comment_id": element.get("parentComment")
        })

    return JsonResponse(
        {
            "ugc_post_urn": ugc_post_urn,
            "total_comments": len(comments),
            "comments": comments
        },
        safe=False
    )

from django.http import JsonResponse
from utils.facebook import get_insta_user_id

def get_insta_user_id_view(request):
    token = request.GET.get("token")
    page_id = request.GET.get("page_id")

    if not token or not page_id:
        return JsonResponse(
            {"error": "token and page_id required"},
            status=400
        )

    insta_id = get_insta_user_id(token, page_id)

    if not insta_id:
        return JsonResponse(
            {"error": "Instagram business account not found"},
            status=404
        )

    return JsonResponse({"instagram_user_id": insta_id})




from utils.facebook import (
    get_facebook_likes_count,
    get_facebook_comments_count,
    get_share_count
)

from api_tokens import FACEBOOK_TOKEN, INSTAGRAM_TOKEN, LINKEDIN_TOKEN

def normalize_url(url):
    if not url:
        return ""

    url = url.strip().lower()
    url = url.replace("www.", "")
    url = url.split("?")[0]

    if url.endswith("/"):
        url = url[:-1]

    return url


# @csrf_exempt
# def fetch_post_stats(request):
#     data = json.loads(request.body)

#     platform = data.get("platform")
#     incoming_url = normalize_url(data.get("post_url"))

#     posts = Post.objects.all()

#     post = None

#     for p in posts:
#         if platform == "instagram" and normalize_url(p.Ipost_url) == incoming_url:
#             post = p
#             break

#         elif platform == "facebook" and normalize_url(p.Fposturl) == incoming_url:
#             post = p
#             print("Checking DB FB URL:", p.Fposturl)
#             print("Normalized DB:", normalize_url(p.Fposturl))
#             break

#         elif platform == "linkedin" and normalize_url(p.Lposturl) == incoming_url:
#             post = p
#             break

#     if not post:
#         print("POST NOT FOUND:", incoming_url)
#         return JsonResponse({"likes": 0, "comments": 0, "shares": 0})

#     if platform == "facebook":
#         stats = fetch_facebook_stats(post)

#     elif platform == "instagram":
#         stats = fetch_instagram_stats(post)

#     elif platform == "linkedin":
#         stats = fetch_linkedin_stats(post)

#     else:
#         stats = {"likes": 0, "comments": 0, "shares": 0}

#     return JsonResponse(stats)


# def fetch_facebook_stats(post):
    
#     if not post.fbpostid:
#         return {"likes": 0, "comments": 0, "shares": 0, "views": 0}

#     # -----------------------------
#     # STEP 1 → Fetch Post Info
#     # -----------------------------
#     url = f"https://graph.facebook.com/v19.0/{post.fbpostid}"

#     params = {
#         "fields": "reactions.summary(true),comments.summary(true),shares,attachments{media,type}",
#         "access_token": FACEBOOK_TOKEN
#     }

#     res = requests.get(url, params=params)
#     data = res.json()

#     print("FB POST RESPONSE:", data)

#     likes = data.get("reactions", {}).get("summary", {}).get("total_count", 0)
#     comments = data.get("comments", {}).get("summary", {}).get("total_count", 0)
#     shares = data.get("shares", {}).get("count", 0)

#     # -----------------------------
#     # STEP 2 → Detect Video
#     # -----------------------------
#     video_id = None

#     try:
#         attachments = data.get("attachments",{}).get("data",[])[0]


#         if attachments.get("media", {}).get("type") == "video":
#             video_id = attachments.get("target",{}).get("id")
        
#         if not video_id:
#             video_id = attachments.get("media",{}).get("id")

#     except Exception:
#         pass

#     # -----------------------------
#     # STEP 3 → Fetch Video Insights
#     # -----------------------------
#     views = 0

#     if video_id:
#         insight_url = f"https://graph.facebook.com/v19.0/{video_id}/insights"

#         insight_params = {
#             "metric": "total_video_views",
#             "access_token": FACEBOOK_TOKEN
#         }

#         insight_res = requests.get(insight_url, params=insight_params).json()

#         print("VIDEO INSIGHTS:", insight_res)

#         try:
#             for item in insight_res.get("data", []):
#                 if item["name"] == "total_video_views":
#                     views = item["values"][0]["value"]
#         except Exception:
#             pass

#     return {
#         "likes": likes,
#         "comments": comments,
#         "shares": shares,
#         "views": views
#     }


# def fetch_instagram_stats(post):
#     url = f"https://graph.facebook.com/v19.0/{post.instapostid}"
#     params = {
#         "fields": "like_count,comments_count",
#         "access_token": INSTAGRAM_TOKEN
#     }

#     r = requests.get(url, params=params).json()

#     return {
#         "likes": r.get("like_count", 0),
#         "comments": r.get("comments_count", 0),
#         "shares": "NA"
#     }

def fetch_linkedin_stats(post):
    if not post.lnpostid:
        return{"likes":0,"comments":0,"shares":0}
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}"
    }

    lnpostid = post.lnpostid

    # Ensure URN format
    if not lnpostid.startswith("urn:li:"):
        lnpostid = f"urn:li:ugcPost:{lnpostid}"

    encoded_urn = urllib.parse.quote(lnpostid)

    url = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}"

    r = requests.get(url, headers=headers).json()

    print("LinkedIn RAW:", r)

    return {
        "likes": r.get("likesSummary", {}).get("totalLikes", 0),
        "comments": r.get("commentsSummary", {}).get("totalComments", 0),
        "shares": 0
    }



def linkedin_callback(request):
    code = request.GET.get("code")

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": "7792cig37u40k6",
        "client_secret": "WPL_AP1.PrvuaBrA0PVJdBCs.Fi63og==",
        "redirect_uri": "http://127.0.0.1:8000/social/linkedin/callback"
    }

    response = requests.post(token_url, data=data)

    return HttpResponse(response.text)

def linkedin_login(request):

    client_id = "7792cig37u40k6"
    redirect_uri = "http://127.0.0.1:8000/social/linkedin/callback"

    scope = "openid profile email w_member_social"

    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )

def affiliate_post_stats(request):
    
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return redirect("affiliate_login")

    # Using SAME logic as SuperAdmin to fetch scraped data
    posts = Post.objects.all().order_by("-created_at").prefetch_related(
        'scrapes__likes', 
        'scrapes__comments'
    )

    # Organize scraped data for easy access in template
    for post in posts:
        post.scraped_info = {s.platform: s for s in post.scrapes.all()}

    return render(
        request,
        "affiliate_post_stats.html",
        {
            "posts": posts
        }
    )


#Affiliate User Action on post for Post Details
def affiliate_post_status(request, post_id):
    
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse({"error":"Not logged in"},status=403)

    affiliate = AffiliateProfile.objects.get(id=affiliate_id)

    data = {
        "likes": list(
            Like.objects.filter(
                affiliate=affiliate,
                post_id=post_id
            ).values_list("platform",flat=True)
        ),

        "comments": list(
            Comment.objects.filter(
                affiliate=affiliate,
                post_id=post_id
            ).values_list("platform",flat=True)
        ),

        "shares": list(
            Share.objects.filter(
                affiliate=affiliate,
                post_id=post_id
            ).values_list("platform",flat=True)
        )
    }

    return JsonResponse(data)


@csrf_exempt
def save_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse({"error": "Not logged in"}, status=403)

    data = json.loads(request.body)

    post_id = data.get("post_id")
    platform = data.get("platform")
    action = data.get("action")

    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)

    if action == "like":
        Like.objects.get_or_create(
            affiliate=affiliate,
            post=post,
            platform=platform
        )

    elif action == "comment":
        Comment.objects.get_or_create(
            affiliate=affiliate,
            post=post,
            platform=platform,
            text="Done"
        )

    elif action == "share":
        Share.objects.get_or_create(
            affiliate=affiliate,
            post=post,
            platform=platform
        )

    return JsonResponse({"status": "success"})
@require_GET
def get_actions(request):
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse({"error": "Not logged in"}, status=403)

    likes = list(
        Like.objects.filter(affiliate_id=affiliate_id)
        .values_list("post_id", flat=True)
    )

    comments = list(
        Comment.objects.filter(affiliate_id=affiliate_id)
        .values_list("post_id", flat=True)
    )

    shares = list(
        Share.objects.filter(affiliate_id=affiliate_id)
        .values_list("post_id", flat=True)
    )

    return JsonResponse({
        "likes": likes,
        "comments": comments,
        "shares": shares
    })


from django.contrib.auth.decorators import login_required

def get_affiliate_actions(request):
    
    affiliate_id = request.session.get("affiliate_id")
    
    if not affiliate_id:
        return JsonResponse({"likes": [], "comments": [], "shares": []})

    try:
        affiliate = AffiliateProfile.objects.get(username=affiliate_id)
    except AffiliateProfile.DoesNotExist:
         return JsonResponse({"likes": [], "comments": [], "shares": []})

    likes = Like.objects.filter(affiliate=affiliate).values_list("post_id", flat=True)
    comments = Comment.objects.filter(affiliate=affiliate).values_list("post_id", flat=True)
    shares = Share.objects.filter(affiliate=affiliate).values_list("post_id", flat=True)

    return JsonResponse({
        "likes": list(likes),
        "comments": list(comments),
        "shares": list(shares)
    })


@login_required
def post_details(request, post_id, platform, type):
    """
    View to display detailed list of likers or commenters for a post and platform
    Separated into Affiliate Users and Other Users
    """
    post = get_object_or_404(Post, id=post_id)
    
    affiliates_found = []
    others_found = []
    scraped_at = None
    
    # Validate inputs
    platform = platform.lower()
    type = type.lower()
    
    if platform not in ['instagram', 'facebook', 'linkedin']:
        messages.error(request, "Invalid platform")
        return redirect('post_stats')
        
    if type not in ['likes', 'comments']:
        messages.error(request, "Invalid type")
        return redirect('post_stats')
    
@login_required
def post_details(request, post_id, platform, type):
    """
    View to display detailed list of likers or commenters for a post and platform
    Separated into Affiliate Users and Other Users
    Includes Cross-Platform Engagement stats for Affiliates
    """
    post = get_object_or_404(Post, id=post_id)
    
    affiliates_found = []
    others_found = []
    scraped_at = None
    
    # Validate inputs
    platform = platform.lower()
    type = type.lower()
    
    if platform not in ['instagram', 'facebook', 'linkedin']:
        messages.error(request, "Invalid platform")
        return redirect('post_stats')
        
    if type not in ['likes', 'comments']:
        messages.error(request, "Invalid type")
        return redirect('post_stats')
    
    # 1. Build map: username (lower) -> affiliate object
    # We need this to identify which affiliate valid user is
    affiliate_map = {} 
    
    affiliates = AffiliateProfile.objects.all()
    for aff in affiliates:
        # Map verified usernames to affiliate
        if aff.instagram_username:
            affiliate_map[aff.instagram_username.lower().strip()] = aff
        if aff.facebook_username:
            affiliate_map[aff.facebook_username.lower().strip()] = aff
        if aff.linkedin_username:
            affiliate_map[aff.linkedin_username.lower().strip()] = aff
            
        # Also map system username as fallback
        affiliate_map[aff.username.lower().strip()] = aff

    # 2. Prepare Cross-Platform Data
    # Fetch all scraped data for this post to check engagement elsewhere
    cross_platform_data = {
        'instagram': {'likes': set(), 'comments': set()},
        'facebook': {'likes': set(), 'comments': set()},
        'linkedin': {'likes': set(), 'comments': set()},
    }
    
    all_scrapes = ScrapedPost.objects.filter(post=post).prefetch_related('likes', 'comments')
    for sp in all_scrapes:
        p = sp.platform
        if p in cross_platform_data:
            # Add all usernames to sets for O(1) lookup
            cross_platform_data[p]['likes'].update(
                list(sp.likes.values_list('username', flat=True))
            )
            cross_platform_data[p]['comments'].update(
                list(sp.comments.values_list('username', flat=True))
            )

    # Helper to check engagement
    def check_engagement(aff, target_platform):
        p_username = None
        if target_platform == 'instagram':
            p_username = aff.instagram_username
        elif target_platform == 'facebook':
            p_username = aff.facebook_username
        elif target_platform == 'linkedin':
            p_username = aff.linkedin_username
            
        if not p_username:
            p_username = aff.username # Fallback
            
        p_username = p_username.lower().strip()
        
        # Check against sets
        # Note: Scraped usernames might differ slightly, but we use strict match for now
        # Ideally we'd normalize both sides
        # We check both specific username and system username against scraped data
        
        # We need to check if ANY of the affiliate's aliases are in the set
        # But for now let's assume p_username is the correct one
        
        # Actually, let's just check the p_username
        has_liked = False
        has_commented = False
        
        # Check if username is in the set (case insensitive handled by lowercasing sets? No, need to lowercase sets content)
        # Let's assume sets have raw data. We should lowercase them?
        # Yes, let's lowercase the sets content in step 2.
        
        # (See update below for lowercasing)
        
        return {
            'liked': p_username in cross_platform_data[target_platform]['likes'],
            'commented': p_username in cross_platform_data[target_platform]['comments']
        }

    # Normalize sets to lowercase
    for p in cross_platform_data:
        cross_platform_data[p]['likes'] = {u.lower().strip() for u in cross_platform_data[p]['likes']}
        cross_platform_data[p]['comments'] = {u.lower().strip() for u in cross_platform_data[p]['comments']}


    # 3. Get Items for CURRENT view
    scraped_post = ScrapedPost.objects.filter(
        post=post, 
        platform=platform
    ).order_by('-scraped_at').first()
    
    if scraped_post:
        scraped_at = scraped_post.scraped_at
        items = []
        
        if type == 'likes':
            items = ScrapedLike.objects.filter(scraped_post=scraped_post)
        else:
            items = ScrapedComment.objects.filter(scraped_post=scraped_post)
            
        # Split and Enrich
        for item in items:
            item_username_lower = item.username.lower().strip()
            
            if item_username_lower in affiliate_map:
                aff = affiliate_map[item_username_lower]
                
                # Check cross platform stats
                ig_status = check_engagement(aff, 'instagram')
                fb_status = check_engagement(aff, 'facebook')
                li_status = check_engagement(aff, 'linkedin')
                
                affiliates_found.append({
                    'username': item.username, # Scraped name
                    'system_username': aff.username, # System name
                    'comment_text': getattr(item, 'comment_text', None),
                    'engagement': {
                        'instagram': ig_status,
                        'facebook': fb_status,
                        'linkedin': li_status
                    }
                })
            else:
                others_found.append(item)
            
    context = {
        'post': post,
        'platform': platform,
        'type': type,
        'affiliates_found': affiliates_found,
        'others_found': others_found,
        'scraped_at': scraped_at
    }
    
    return render(request, 'post_details.html', context)
