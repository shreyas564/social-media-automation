import requests
import urllib.parse
from django.http import JsonResponse
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
from django.shortcuts import get_object_or_404
from .models import Post, Like, Comment, Share, AffiliateProfile
from utils.cloudConnect import upload_image_to_cloudinary    
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password, make_password
from .models import AffiliateProfile, Post
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import AffiliateProfile
#from utils.facebook import *
from django.views.decorators.http import require_GET
from .models import Post, SuperAdmin, InstagramComment
from utils.facebook import get_insta_user_id
from django.http import JsonResponse


N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/social-post"
#sending image

FBTOKEN="EAAMcHkCZAkvIBQizcNQy6srhlnCNTjkghxjTSylFREOzeCoNFpyFDWO7ZA8wZCzm1cIINl919eM9o1oUbyaCwbiwE1ZC6r90wgjZA5xHlpGFEQh5LG8Gw5dvEnQqRmGXg6Fl6EmKbtL8QMqmb4jLZBcZBeZBepThlJ0iRPZCWjiAg0oMH10J8uOkJO1Jrf6jev2URpRI0bZBOh7n01rk4w7UyT4PzUlfmmS6fcGtTKI9q8V25ZA"

N8N_Image_Url="http://localhost:5678/webhook-test/image-url"

def send_imageurl(image_url) :
    payload = {
        "image_url": image_url
    }

    try:
        response = requests.post(
            N8N_Image_Url,
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

def send_image_to_n8n(image_url, caption,post_id,post_name="") :
    
    payload = {
        "image_url": image_url,
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



def create_post(request):
    return render(request, 'createpost.html')


def post_submitted(request):
    print("Post submission received")
    if request.method == "POST":
        image = request.FILES.get("post_image")
        caption = request.POST.get("post_text")
        post_name = request.POST.get("post_name")
        user=request.POST.get("user_id") 


        print("Admin User ID:", user)
        if not image or not caption:
            return JsonResponse({
                "success": False,
                "message": "Image and caption are required"
            }, status=400)

        try:
            super_admin = request.user.super_admin
        except SuperAdmin.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Only SuperAdmins can create posts"
            }, status=403)


        image_url = upload_image_to_cloudinary(image)

        
        post = Post.objects.create(
            image=image,   # optional if you want local storage
            caption=caption,
            post_name=post_name,
            created_by=super_admin
        )
         # type: ignore
        post_id = post.id # type: ignore
        print("Post created with ID:", post_id)
        print("Image uploaded to Cloudinary:", image_url)
        send_imageurl(image_url)
        return send_image_to_n8n(image_url, caption,post.id,post_name) # type: ignore
    else:
        JsonResponse({"error": "Invalid method"}, status=405)


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
    return JsonResponse({"status":"succcess"})

def share_post(request):
    affiliate_id = request.session.get("affiliate_id")
    post_id = request.POST.get("post_id")
    platform = request.POST.get("platform")
    affiliate = AffiliateProfile.objects.get(id=affiliate_id)
    post = Post.objects.get(id=post_id)
    Share.objects.create(affiliate = affiliate,post=post,platform=platform)
    return JsonResponse({"status":"success"})


#for affiliate regestration side
@require_POST
def affiliate_like_post(request):
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse(
            {"error": "Affiliate not logged in"},
            status=403
        )

    post_id = request.POST.get("post_id")

    if not post_id:
        return JsonResponse(
            {"error": "Post ID missing"},
            status=400
        )

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        affiliate=affiliate,
        post=post
    )

    if not created:
        return JsonResponse({
            "status": "already_liked",
            "message": "You already liked this post"
        })

    return JsonResponse({
        "status": "success",
        "message": "Post liked successfully"
    })



# COMMENT POST
@require_POST
def affiliate_comment_post(request):
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse(
            {"error": "Affiliate not logged in"},
            status=403
        )

    post_id = request.POST.get("post_id")
    comment_text = request.POST.get("comment_text")

    if not post_id or not comment_text:
        return JsonResponse(
            {"error": "Post ID or comment missing"},
            status=400
        )

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    post = get_object_or_404(Post, id=post_id)

    Comment.objects.create(
        affiliate=affiliate,
        post=post,
        text=comment_text
    )

    return JsonResponse({
        "status": "success",
        "message": "Comment added successfully"
    })


# SHARE POST
@require_POST
def affiliate_share_post(request):
    affiliate_id = request.session.get("affiliate_id")

    if not affiliate_id:
        return JsonResponse(
            {"error": "Affiliate not logged in"},
            status=403
        )

    post_id = request.POST.get("post_id")
    platform = request.POST.get("platform")

    if not post_id or not platform:
        return JsonResponse(
            {"error": "Post ID or platform missing"},
            status=400
        )

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    post = get_object_or_404(Post, id=post_id)

    Share.objects.create(
        affiliate=affiliate,
        post=post,
        platform=platform
    )

    return JsonResponse({
        "status": "success",
        "message": "Post shared successfully"
    })

#  AFFILIATE SETTINGS PAGE
def usersettings(request):
    affiliate_id = request.session.get('affiliate_id')
    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
    return render(request, 'affiliatesettings.html', {'affiliate': affiliate})


# AFFILIATE PROFILE PAGE
# def affiliate_profile(request):
#     affiliate_id = request.session.get('affiliate_id')
#     if not affiliate_id:
#         return redirect('affiliate_login')

#     affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)
#     return render(request, 'affiliate_profile.html', {'affiliate': affiliate})

#UPDATE AFFILIATE PROFILE (POST)
@require_POST
def update_affiliate_profile(request):
    affiliate_id = request.session.get('affiliate_id')

    if not affiliate_id:
        return redirect('affiliate_login')

    affiliate = get_object_or_404(AffiliateProfile, id=affiliate_id)

    affiliate.username = request.POST.get("username", affiliate.username)

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





# Affiliate post action
# def affiliate_post_actoion(request):
#     if request.method == "POST":
#          affiliate_post_actoion.objects.create(                         #Affiliate_post_action.objects
#              affiliate_username = request.Post.get('username'),
#              post_id = request.POST.get('post_id'),
#              action = request.POST.get('actio'),
#              comment_text = request.POST.get('comment','')
#          )
#          return JsonResponse({'status': 'success'})
    


#SUPER ADMIN SIDE 
def posts_list(request):
     posts = Post.objects.all().order_by('-created_at')
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
    affiliate_profiles = AffiliateProfile.objects.all()
    return render(request, 'affiliateusers.html', {'users': affiliate_profiles})

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

def submit_editpost(request,post_id):
    if request.method == "POST":
        caption = request.POST.get("caption")
        post=Post.objects.get(id=post_id)
        post.caption=caption
        post.save()
        send_caption_to_n8n(caption)
        #messages.success(request, "Post updated successfully")
        return redirect('posts_list')
    
def del_post(request,post_id):
    post=Post.objects.get(id=post_id)
    super_admin=SuperAdmin.objects.get(id=request.user.id)
    user=super_admin
    resF=delete_facebook_post(post.fbpostid,user.fbtoken)
    resI=delete_instagram_post(post.instapostid, user.instatoken)       
    resL=delete_linkedin_post(post.lnpostid, user.lntoken)
    print("Facebook Deletion Response:", resF)
    print("Instagram Deletion Response:", resI)
    print("LinkedIn Deletion Response:", resL)
    post.delete()
    print("Posts deleted successfully")
    return redirect('posts_list')

def logout_view(request):
    logout(request)
    return redirect('log_admin')

# @csrf_exempt
# def collect_post_data(request):
#     if request.method != "POST":
#         return JsonResponse(
#             {"error": "Invalid method"},
#             status=405
#         )

#     try:
#         body = json.loads(request.body.decode("utf-8"))
#     except json.JSONDecodeError:
#         return JsonResponse(
#             {"error": "Invalid JSON payload"},
#             status=400
#         )

#     posts = body.get("posts")
#     caption= body.get("caption")

#     if not isinstance(posts, list):
#         return JsonResponse(
#             {"error": "`posts` must be a list"},
#             status=400
#         )

#     for post in posts:
#         platform = post.get("platform")
#         pst=Post.objects.get(id=post.get("postid"))
#         pst.caption=caption
#         pst.Ipost_url=post.get("Ipost_url")
#         pst.Fposturl=post.get("Fposturl")
#         pst.Lposturl=post.get("Lposturl")

#         print(post.get("Ipost_url"))
#         print(post.get("Fposturl"))
#         print(post.get("Lposturl"))
#         match platform:
#             case "facebook":
#                 pst.fbpostid=post.get("post_id")
#                 pst.save()
#             case "instagram":
#                 pst.instapostid=post.get("post_id")
#                 pst.save()
#             case "linkedin":
#                 pst.lnpostid=post.get("post_id")
#                 pst.save()

#     return JsonResponse(
#         {
#             "status": "success",
#             "data": posts
#         },
#         status=200
#     )
@csrf_exempt
def collect_post_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    payload = json.loads(request.body)
    posts = payload.get("posts", [])
    caption = payload.get("caption")  # 🔥 AI GENERATED caption

    updated = set()

    for item in posts:
        post_id = item.get("postid")
        platform = item.get("platform")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            continue

        # ✅ update caption ONCE
        if caption and post.id not in updated:
            post.caption = caption
            updated.add(post.id)

        # PLATFORM FIELDS
        if platform == "facebook":
            post.fbpostid = item.get("post_id")
            post.Fposturl = item.get("Fposturl")

        elif platform == "instagram":
            post.instapostid = item.get("post_id")
            post.Ipost_url = item.get("Ipost_url")

        elif platform == "linkedin":
            post.lnpostid = item.get("post_id")
            post.Lposturl = item.get("Lposturl")

        post.save()

    return JsonResponse({
        "status": "success",
        "updated_posts": list(updated)
    })



def delete_facebook_post(post_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{post_id}"
    response = requests.delete(url, params={"access_token": access_token})
    return response.json()


def delete_instagram_post(media_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    response = requests.delete(url, params={"access_token": access_token})
    return response.json()



def delete_linkedin_post(post_urn, access_token):
    if not post_urn:
        return {"error": "post_urn is empty"}

    # Ensure string
    post_urn = str(post_urn)

    # Ensure full URN
    if not post_urn.startswith("urn:li:"):
        post_urn = f"urn:li:ugcPost:{post_urn}"

    # Encode URN
    encoded_urn = urllib.parse.quote(post_urn, safe="")

    url = f"https://api.linkedin.com/v2/ugcPosts/{encoded_urn}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    response = requests.delete(url, headers=headers)

    return {
        "status_code": response.status_code,
        "response": response.text or "Deleted"
    }

# @login_required
# def postStat(request):
#     posts = Post.objects.filter(
#         fbpostid__isnull=False
#     ).exclude(fbpostid="")

#     for post in posts:
#         try:
#             post.total_likes = get_facebook_likes_count(
#                 post.fbpostid, FBTOKEN
#             )
#             post.total_comments = get_facebook_comments_count(
#                 post.fbpostid, FBTOKEN
#             )
#             post.total_shares = get_share_count(
#                 post.fbpostid, FBTOKEN
#             )
#             post.save()

#         except Exception as e:
#             print(f"Failed for post {post.id}: {e}")

#     return render(
#         request,
#         "postStat.html",
#         {"posts": posts}
#     )
# @login_required
# def postStat(request):
#     posts = Post.objects.filter(
#         fbpostid__isnull=False
#     ).exclude(fbpostid="")

#     print("POSTS FOUND:", posts.count())

#     for post in posts:
#         print("FETCHING STATS FOR FB POST ID:", post.fbpostid)

#         post.total_likes = get_facebook_likes_count(
#             post.fbpostid, FBTOKEN
#         )
#         post.total_comments = get_facebook_comments_count(
#             post.fbpostid, FBTOKEN
#         )
#         post.total_shares = get_share_count(
#             post.fbpostid, FBTOKEN
#         )

#         print(
#             "LIKES:", post.total_likes,
#             "COMMENTS:", post.total_comments,
#             "SHARES:", post.total_shares
#         )

#         post.save()

#     return render(
#         request,
#         "postStat.html",
#         {"posts": posts}
#     )

@login_required
def postStat(request):
    posts = Post.objects.all().order_by('-created_at')

    return render(
        request,
        "postStat.html",
        {"posts": posts}
    )

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


def post_stats_view(request):
    posts = Post.objects.all()   

    print("POST COUNT:", posts.count())  

    return render(
        request,
        "social/postStat.html",
        {"posts": posts}
    )


# ---------------- FACEBOOK ----------------
def get_facebook_stats(post_id):
    url = f"{FB_BASE_URL}/{post_id}"
    params = {
        "fields": "reactions.summary(true),comments.summary(true),shares",
        "access_token": FB_ACCESS_TOKEN
    }

    res = requests.get(url, params=params).json()

    return {
        "likes": res.get("reactions", {}).get("summary", {}).get("total_count", 0),
        "comments": res.get("comments", {}).get("summary", {}).get("total_count", 0),
        "shares": res.get("shares", {}).get("count", 0),
    }


# ---------------- INSTAGRAM ----------------
def get_instagram_stats(media_id):
    # Instagram Graph API
    url = f"{FB_BASE_URL}/{media_id}"
    params = {
        "fields": "like_count,comments_count",
        "access_token": FB_ACCESS_TOKEN
    }

    res = requests.get(url, params=params).json()

    return {
        "likes": res.get("like_count", 0),
        "comments": res.get("comments_count", 0),
        "shares": 0  # Instagram does not provide share count
    }


# ---------------- LINKEDIN (LIMITATION) ----------------
def get_linkedin_stats():
    # LinkedIn does NOT allow public stats via API
    return {
        "likes": 0,
        "comments": 0,
        "shares": 0
    }


# ---------------- AJAX HANDLER ----------------
# views.py
from django.http import JsonResponse
from utils.facebook import (
    get_facebook_likes_count,
    get_facebook_comments_count,
    get_share_count
)

FBTOKEN="EAAMcHkCZAkvIBQmgeWZAOZAtYLn0kNdjGlkefFmYf5T5WNE9z3vMK3oCDQ6thSYxvPXJ6qjCTYsbaFjGXO28RLRbqn5aDqonTqV9UEF3O28trT2LhobR9AUcObfl0IZC8dLo9d8QnJnwVjnJ0n69qqnD1BGAL3qnkAFy2a9dnpfyCHaM1lEcgIeJF2erd2cHJ4LYnPzJ4ffuSUaFPvVlu0lcC04zHycSXK7kzSEZD"
#FBTOKEN = OS.getenv("FBTOKEN", FBTOKEN)

def fetch_post_stats(request):
    post_id = request.GET.get("post_id")
    platform = request.GET.get("platform")

    likes = comments = shares = 0

    try:
        if platform == "Instagram":
            likes = get_facebook_likes_count(post_id, FBTOKEN)
            comments = get_facebook_comments_count(post_id, FBTOKEN)
            shares = 0  # IG doesn't support shares
        elif platform == "LinkedIn":
            # placeholder until LinkedIn API
            likes = comments = shares = 0

        return JsonResponse({
            "likes": likes,
            "comments": comments,
            "shares": shares
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



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



ACCESS_TOKEN = "AQVmKq7AGLBhnyazWkRWx2RMweRK8PqQSafJrzSJ36fTqNcbvhWM4q7qZy1rSpughTTfuWF0Ar6D4hY_syoAkWmlPXAjZahrpn_mE7g_PsMFqOGwJiewVuKxY8puHZXrn-rMFMT6M3K2_6NQioNOiCc0VEwZYYVgHWDc4CEbHxGmquMp2An34LOkr79joe6milnWWnefeWrsqKErWX87oPQt75UidiX5YfRXZeXWsS-EJSXAJ7TYhua6gRiIxNxTup0yTaM3dqLReuXXlezzRni5kNBD9Npidv3cPlCzA-3wmCnv6-1L5iGBrJ8UezBk1pW1bfjKiCHfnGtpDiN08J8cvZoz2Q"
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


# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def fetch_post_stats(request):
#     data = json.loads(request.body)

#     platform = data.get("platform")
#     post_url = data.get("post_url")

#     if platform == "instagram":
#         return JsonResponse(get_instagram_stats(post_url))

#     if platform == "facebook":
#         return JsonResponse(get_facebook_stats(post_url))

#     if platform == "linkedin":
#         return JsonResponse(get_linkedin_stats(post_url))

#     return JsonResponse({"likes": 0, "comments": 0, "shares": 0})
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.facebook import (
    get_facebook_likes_count,
    get_facebook_comments_count,
    get_share_count
)
from utils.linkedin import get_linkedin_stats
from utils.instagram import get_instagram_stats  # if exists


@csrf_exempt
def fetch_post_stats(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    body = json.loads(request.body)
    platform = body.get("platform")
    post_url = body.get("post_url")

    # SAFETY
    if not platform or not post_url:
        return JsonResponse({"likes": 0, "comments": 0, "shares": 0})

    # 🔵 FACEBOOK
    if platform == "facebook":
        post_id = post_url.split("/")[-1]  # basic extraction
        likes = get_facebook_likes_count(post_id, request.user.super_admin.fbtoken)
        comments = get_facebook_comments_count(post_id, request.user.super_admin.fbtoken)
        shares = get_share_count(post_id, request.user.super_admin.fbtoken)

        return JsonResponse({
            "likes": likes,
            "comments": comments,
            "shares": shares
        })

    # 🟣 INSTAGRAM
    if platform == "instagram":
        stats = get_instagram_stats(post_url)
        return JsonResponse(stats)

    # 🔵 LINKEDIN
    if platform == "linkedin":
        stats = get_linkedin_stats(post_url)
        return JsonResponse(stats)

    return JsonResponse({"likes": 0, "comments": 0, "shares": 0})
