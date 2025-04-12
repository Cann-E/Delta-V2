from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.dispatch import receiver  # ✅ Import receiver to handle signals
from django.db.models.signals import post_save  # ✅ Import post_save signal
from delta.pdf_utils import generate_pdf_for_request  # ✅ Import PDF generation function


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
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20)

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)

    current_major = models.CharField(max_length=100, blank=True, null=True)
    new_major = models.CharField(max_length=100, blank=True, null=True)
    old_address = models.CharField(max_length=255, blank=True, null=True)
    new_address = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    date_created = models.DateField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='generated_pdfs/', blank=True, null=True)


    def save(self, *args, **kwargs):
        """ Auto-fill first_name and last_name from user session before saving """
        if not self.first_name:
            self.first_name = self.user.first_name
        if not self.last_name:
            self.last_name = self.user.last_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.request_type} ({self.status})"
#NAM2    
class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To: {self.recipient.username} - {self.message[:40]}"    
#Notify admins when users sign up a new account    
@receiver(post_save, sender=CustomUser)
def notify_admins_on_new_signup(sender, instance, created, **kwargs):
    if created:
        from .models import Notification  # Avoid circular import
        admins = CustomUser.objects.filter(role='admin', is_active=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                message=f"🆕 New user registered: {instance.username} ({instance.email})"
            )

class GeneralPetition(models.Model):#FOR INTEGRATION
    # Student Information Section
    student_last_name = models.CharField(max_length=100)
    student_first_name = models.CharField(max_length=100)
    student_middle_name = models.CharField(max_length=100, blank=True, null=True)
    student_uh_id = models.CharField(max_length=20)
    student_phone_number = models.CharField(max_length=20, blank=True, null=True)
    student_program_plan = models.CharField(max_length=100)
    student_academic_career = models.CharField(max_length=100)
    student_mailing_address = models.TextField()
    student_city = models.CharField(max_length=100)
    student_state = models.CharField(max_length=50)
    student_zip_code = models.CharField(max_length=10)
    student_email = models.EmailField()

    # Petition Purposes
    program_status_action = models.CharField(max_length=100, blank=True, null=True)
    admission_status_from = models.CharField(max_length=100, blank=True, null=True)
    admission_status_to = models.CharField(max_length=100, blank=True, null=True)
    new_career = models.CharField(max_length=100, blank=True, null=True)
    post_bac_study_objective = models.CharField(max_length=100, blank=True, null=True)
    second_bachelor_plan = models.BooleanField(default=False)
    graduate_study_objective = models.BooleanField(default=False)
    teacher_certification = models.BooleanField(default=False)
    personal_enrichment_objective = models.BooleanField(default=False)

    program_change_from = models.CharField(max_length=100, blank=True, null=True)
    program_change_to = models.CharField(max_length=100, blank=True, null=True)

    plan_change_from = models.CharField(max_length=100, blank=True, null=True)
    plan_change_to = models.CharField(max_length=100, blank=True, null=True)

    degree_objective_change_from = models.CharField(max_length=100, blank=True, null=True)
    degree_objective_change_to = models.CharField(max_length=100, blank=True, null=True)

    requirement_term_year = models.CharField(max_length=4, blank=True, null=True)
    requirement_term_catalog = models.CharField(max_length=100, blank=True, null=True)
    requirement_term_career = models.CharField(max_length=100, blank=True, null=True)
    requirement_term_program_plan = models.CharField(max_length=100, blank=True, null=True)

    additional_plan_degree_type = models.CharField(max_length=50, blank=True, null=True)
    is_new_plan_primary_or_secondary = models.CharField(max_length=50, blank=True, null=True)
    other_current_plans_or_minors = models.TextField(blank=True, null=True)

    second_degree_type = models.CharField(max_length=100, blank=True, null=True)

    minor_change_from = models.CharField(max_length=100, blank=True, null=True)
    minor_change_to = models.CharField(max_length=100, blank=True, null=True)

    additional_minor = models.CharField(max_length=100, blank=True, null=True)

    degree_requirement_exception_details = models.TextField(blank=True, null=True)

    special_problems_course_list = models.TextField(blank=True, null=True)

    course_overload_gpa = models.CharField(max_length=10, blank=True, null=True)
    course_overload_credit_hours = models.CharField(max_length=10, blank=True, null=True)
    course_overload_course_list = models.TextField(blank=True, null=True)

    graduate_leave_of_absence_request_details = models.TextField(blank=True, null=True)
    graduate_reinstatement_request_details = models.TextField(blank=True, null=True)
    other_request_details = models.TextField(blank=True, null=True)

    explanation_of_request = models.TextField(blank=True, null=True)
    student_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    signature_date = models.DateField(blank=True, null=True)

    date_submitted = models.DateField(auto_now_add=True)


