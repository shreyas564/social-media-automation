from .models import AdminNotification, SuperAdmin


def admin_notifications(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}

    super_admin = SuperAdmin.objects.filter(user=request.user).first()
    if not super_admin:
        return {}

    unread_qs = AdminNotification.objects.filter(super_admin=super_admin, is_read=False)
    return {
        "admin_unread_notification_count": unread_qs.count(),
        "admin_unread_notifications": unread_qs[:5],
    }

def global_settings(request):
    # Always read from the primary super admin for global consistency
    super_admin = SuperAdmin.objects.first()
    if super_admin:
        return {
            "currency": super_admin.currency,
            "currency_symbol": super_admin.currency_symbol,
        }
    return {
        "currency": "INR",
        "currency_symbol": "₹",
    }
