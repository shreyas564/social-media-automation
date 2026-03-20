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
    path("log-admin/", views.log_admin, name="log_admin"),
    path("auth-admin/", views.auth_admin, name="auth_admin"),
    path("add-superadmin/", views.add_superadmin_page, name="add_superadmin"),
    path("create-superadmin/", views.create_superadmin, name="create_superadmin"),

    path("create-post/", views.create_post, name="create_post"),
    path("post-submitted/", views.post_submitted, name="post_submitted"), # type: ignore
    path("posts-list/", views.posts_list, name="posts_list"),

    path("edit-post/<int:post_id>", views.editpost, name="edit_post"),
    path("submit-edit-post/<int:post_id>", views.submit_editpost, name="submit_edit_post"), # type: ignore
    path("delete-post/<int:post_id>", views.del_post, name="delete_post"),

    path("users/", views.affiliate_users, name="affiliate_users"),
    
    # Verification Dashboard
    path("verification/", views.verification_dashboard, name="verification_dashboard"),
    path("verification/trigger/", views.trigger_verification, name="trigger_verification"),
    
    # Post Scraping & Verification
    path("scrape-post/<int:post_id>/", views.scrape_post_data, name="scrape_post"),
    path("verify-post/<int:post_id>/", views.verify_post_data, name="verify_post"),
    
    path("settings/", views.setting, name="settings"),
    path("payment-settings/", views.payment_settings, name="payment_settings"),
    path("payment-history/", views.payment_history, name="payment_history"),
    path("affiliate-wallet/", views.affiliate_wallet, name="affiliate_wallet"),
    path("withdrawal-requests/", views.withdrawal_requests, name="withdrawal_requests"),
    path("withdrawal-requests/update/", views.update_withdrawal_request_status, name="update_withdrawal_request_status"),
    path("profile/", views.profile, name="profile"),
    path("update-profile/", views.update_admin_profile, name="update_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("update-password/", views.update_password, name="update_password"),
    path("logout/", views.logout_view, name="logout"),
    path("post-stats/", views.postStat, name="post_stats"),
    path("post-stats/sync/", views.sync_post_stats, name="sync_post_stats"),
    path("post-stats/sync/<int:post_id>/", views.sync_single_post_stats, name="sync_single_post_stats"),
    path("post-details/<int:post_id>/<str:platform>/<str:type>/", views.post_details, name="post_details"),
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
    #path("post-stats/", views.post_stats_view, name="post_stats"),
    #path("fetch-stats/", views.fetch_post_stats, name="fetch_post_stats"),
    #path("fetch-post-stats/", views.fetch_post_stats, name="fetch_post_stats"),
    #path('social/linkedin/callback/', views.linkedin_callback, name='linkedin_callback'),
    path("affiliate/post-stats/", views.affiliate_post_stats, name="affiliate_post_stats"),
    path("affiliate/post-stats/sync/", views.affiliate_sync_post_stats, name="affiliate_sync_post_stats"),
    #path("affiliate-status/<int:post_id>/", views.affiliate_post_status, name="affiliate_post_status"),
    # AFFILIATE ACTION APIs
    path("affiliate/save-action/", views.save_action, name="save_action"),
    path("affiliate/get-actions/", views.get_actions, name="get_actions"),
    path("affiliate/get-affiliate-actions/", views.get_affiliate_actions, name="get_affiliate_actions"),


    # AFFILIATE USER URLS
    path("affiliate-register/", views.affiliate_register, name="affiliate_register"),
    path("affiliate-login/", views.affiliate_login, name="affiliate_login"),
    path("affiliate-dashboard/", views.affiliate_dashboard, name="affiliate_dashboard"),
    path("affiliate/post-details/", views.affiliate_post_details_view, name="affiliate_post_details"),

    path("affiliate/like/", views.like_post, name="like_post"),
    path("affiliate/comment/", views.comment_post, name="comment_post"),
    path("affiliate/share/", views.share_post, name="share_post"),

    path("like_post/", views.like_post, name="like_post"),
    path("comment-post/", views.comment_post, name="comment_post"),
    path("share-post/", views.share_post, name="share_post"),

    path("user/settings/", views.usersettings, name="usersettings"),
    path("affiliate/rewards-settings/", views.affiliate_rewards_settings, name="affiliate_rewards_settings"),
    path("affiliate/withdrawal/", views.affiliate_withdrawal_page, name="affiliate_withdrawal_page"),
    path("affiliate/withdrawal/request/", views.request_withdrawal, name="request_withdrawal"),
    path("affiliate/payment-history/", views.affiliate_payment_history, name="affiliate_payment_history"),
    path("affiliate/user-payment-details/", views.user_payment_details, name="user_payment_details"),
    path("edit-profile/", views.edit_affiliate_profile, name="edit_affiliate_profile"),
    path("affiliate/change-password/", views.change_password_page, name="change_password_page"),
    path("affiliate/update-profile/", views.update_affiliate_profile, name="update_affiliate_profile"),
    path("affiliate/update-password/", views.change_affiliate_password, name="change_affiliate_password"),
    path("affiliate-logout/", views.affiliate_logout, name="affiliate_logout"),

    # AFFILIATE SOCIAL CONNECT (OAuth)
    path("affiliate/connect/facebook/", views.affiliate_connect_facebook, name="affiliate_connect_facebook"),
    path("affiliate/connect/facebook/callback/", views.affiliate_facebook_callback, name="affiliate_facebook_callback"),
    path("affiliate/connect/instagram/", views.affiliate_connect_instagram, name="affiliate_connect_instagram"),
    path("affiliate/connect/instagram/callback/", views.affiliate_instagram_callback, name="affiliate_instagram_callback"),
    path("affiliate/connect/linkedin/", views.affiliate_connect_linkedin, name="affiliate_connect_linkedin"),
    path("affiliate/connect/linkedin/callback/", views.affiliate_linkedin_callback, name="affiliate_linkedin_callback"),
    path("affiliate/disconnect/<str:platform>/", views.affiliate_disconnect_platform, name="affiliate_disconnect_platform"),
]
