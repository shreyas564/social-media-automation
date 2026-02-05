from django.urls import path
from . import views 

urlpatterns = [
    # COMMON / INTEGRATIONS
    path("upload-image/", views.send_image_to_n8n, name="upload_image"),
    path('collect-data/', views.collect_post_data, name='collect_data'),
    path("linkedin/callback", views.linkedin_callback, name="linkedin_callback"),
    path("social/linkedin/login", views.linkedin_login, name="linkedin_login"),



    # SUPER ADMIN URLS
    path("super-admin/", views.superAdmin, name="super_admin"),
    path("admin-registration/", views.admin_registration, name="admin_registration"),
    path("create-admin/", views.create_admin, name="create_admin"),
    path("log-admin/", views.log_admin, name="log_admin"),
    path("auth-admin/", views.auth_admin, name="auth_admin"),

    path("create-post/", views.create_post, name="create_post"),
    path("post-submitted/", views.post_submitted, name="post_submitted"), # type: ignore
    path("posts-list/", views.posts_list, name="posts_list"),

    path("edit-post/<int:post_id>", views.editpost, name="edit_post"),
    path("submit-edit-post/<int:post_id>", views.submit_editpost, name="submit_edit_post"), # type: ignore
    path("delete-post/<int:post_id>", views.del_post, name="delete_post"),

    path("users/", views.affiliate_users, name="affiliate_users"),
    path("settings/", views.setting, name="settings"),
    path("profile/", views.profile, name="profile"),
    path("update-profile/", views.update_admin_profile, name="update_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("update-password/", views.update_password, name="update_password"),
    path("logout/", views.logout_view, name="logout"),
    path("post-stats/", views.postStat, name="post_stats"),
    path("post-likes/<str:postid>/<str:access_token>",views.get_facebook_likes_count,name="like_count"),
    path("post-comment/<str:postid>/<str:access_token>/",views.get_facebook_comments_count,name="comment_count"),
    path("post-share/<str:postid>/<str:access_token>",views.get_share_count,name="share_count"),
    path("create-fb/",views.add_fb_page,name="fbpage"),
    path("save-page/",views.add_page,name="savepage"),
    path("getinsta-likes/<str:ipostid>/<str:token>",views.get_insta_likes_and_comments,name="getinstaLikes"),
    path("getinsta-username/",views.get_insta_user_id_view,name="Iusername"),
    path("getusernames/<str:mediaid>",views.get_insta_user_id,name="Inusernames"),
    path("getfacebook-usernames/<str:postid>/",views.get_facebook_commenters,name="getfacebook_usernames"),
    path("linkedin/comments/<path:ugc_post_urn>/", views.get_linkedin_comments, name="get_linkedin_comments"),
    path("instagram/sync-comments/", views.sync_instagram_comments, name="sync_instagram_comments"),
    path("sync-instagram-comments/", views.sync_instagram_comments),
    path("insta/post-stats/<str:ipostid>/<str:token>/",views.get_insta_likes_and_comments,name="insta_post_stats"),
    path("post-stats/", views.post_stats_view, name="post_stats"),
    path("fetch-stats/", views.fetch_post_stats, name="fetch_post_stats"),
    path("fetch-post-stats/", views.fetch_post_stats, name="fetch_post_stats"),
    #path('social/linkedin/callback/', views.linkedin_callback, name='linkedin_callback'),


    # AFFILIATE USER URLS
    path("affiliate-register/", views.affiliate_register, name="affiliate_register"),
    path("affiliate-login/", views.affiliate_login, name="affiliate_login"),
    path("affiliate-dashboard/", views.affiliate_dashboard, name="affiliate_dashboard"),
    path("affiliate-feed/", views.affiliate_feed, name="affiliate_feed"),

    path("affiliate/like/", views.like_post, name="like_post"),
    path("affiliate/comment/", views.comment_post, name="comment_post"),
    path("affiliate/share/", views.share_post, name="share_post"),

    path("like_post/", views.like_post, name="like_post"),
    path("comment-post/", views.comment_post, name="comment_post"),
    path("share-post/", views.share_post, name="share_post"),

    path("user/settings/", views.usersettings, name="usersettings"),
    path("edit-profile/", views.edit_affiliate_profile, name="edit_affiliate_profile"),
    path("affiliate/change-password/", views.change_password_page, name="change_password_page"),
    path("affiliate/update-profile/", views.update_affiliate_profile, name="update_affiliate_profile"),
    path("affiliate/update-password/", views.change_affiliate_password, name="change_affiliate_password"),
    path("affiliate-logout/", views.affiliate_logout, name="affiliate_logout"),
]