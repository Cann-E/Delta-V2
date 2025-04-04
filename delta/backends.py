from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class AllowInactiveModelBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True  # Allow even inactive users for manual checks
