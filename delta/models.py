from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.dispatch import receiver  # ✅ Import receiver to handle signals
from django.db.models.signals import post_save  # ✅ Import post_save signal
from delta.pdf_utils import generate_pdf_for_request  # ✅ Import PDF generation function
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string


class CustomUser(AbstractUser):
    # Override the inherited groups field
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser',
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )

    # Override the inherited user_permissions field
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser',
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    ROLE_CHOICES = (
        ('basicuser', 'Basic User'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='basicuser')
    status = models.BooleanField(default=True)
    uh_id = models.CharField(max_length=10, blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # NEW: Signature field for users
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.role == 'admin'

    def can_change_request_status(self, request):
        return self.is_admin() or self == request.user

class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('returned', 'Returned'),
    ]
    REQUEST_TYPE_CHOICES = [
        ('change_major', 'Change Major'),
        ('change_address', 'Change Address'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)
    explanation = models.TextField(blank=True, null=True)
    current_major = models.CharField(max_length=100, blank=True, null=True)
    new_major = models.CharField(max_length=100, blank=True, null=True)
    old_address = models.CharField(max_length=255, blank=True, null=True)
    new_address = models.CharField(max_length=255, blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

def save(self, *args, **kwargs):
    print(f"[DEBUG] save() called for Request ID: {self.pk}")
    
    if not self.first_name:
        self.first_name = self.user.first_name
    if not self.last_name:
        self.last_name = self.user.last_name

    is_new = self.pk is None
    previous_status = None

    if not is_new:
        try:
            previous = Request.objects.get(pk=self.pk)
            previous_status = previous.status
        except Request.DoesNotExist:
            previous_status = None

    super().save(*args, **kwargs)

    if (is_new or self.status != previous_status) and self.status in ['pending', 'approved']:
        from .pdf_utils import generate_pdf_for_request
        import os
        from django.conf import settings

        print(f"[DEBUG] Triggering PDF for request ID: {self.pk}, status: {self.status}")
        
        if self.request_type == 'change_major':
            tex_template_path = os.path.join(settings.BASE_DIR, 'PDF/change_major.tex')
        else:
            tex_template_path = os.path.join(settings.BASE_DIR, 'PDF/change_address.tex')

        context = {
            'request': self,
            'user': self.user,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_created': self.date_created,
            'request_type': self.get_request_type_display(),
            'status': self.get_status_display(),
            'current_major': self.current_major,
            'new_major': self.new_major,
            'old_address': self.old_address,
            'new_address': self.new_address,
            'explanation': self.explanation
        }

        output_filename = f'request_{self.pk}.pdf'
        print(f"[DEBUG] Calling generate_pdf_for_request with: {tex_template_path}, {output_filename}")
        path = generate_pdf_for_request(tex_template_path, context, output_filename)
        print(f"[DEBUG] PDF Path returned: {path}")

        if path:
            self.pdf_file.name = os.path.relpath(path, settings.MEDIA_ROOT)
            print(f"[DEBUG] Setting pdf_file field to: {self.pdf_file.name}")
            super().save(update_fields=["pdf_file"])
        else:
            print("[ERROR] PDF generation failed or returned None")


   
class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:20]}"
