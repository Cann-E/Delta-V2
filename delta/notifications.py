from delta.models import Notification, CustomUser

def notify_admins(message):
    admins = CustomUser.objects.filter(is_superuser=True)
    for admin in admins:
        Notification.objects.create(
            recipient=admin,
            message=message
        )
def notify_user(user, message):
    Notification.objects.create(recipient=user, message=message)
