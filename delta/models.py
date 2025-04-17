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
        ('unitapprover', 'Unit Approver'),# new: Approves only requests from their unit
        ('admin', 'Administrator'), # got from is_org_approver, Approves across units
        ('clerk', 'Clerk'),#new: Data entry, can create but not approve requests
        ('auditor', 'Auditor'),#new: Read-only access to track progress or for compliance reporting
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='basicuser')
    is_org_approver = models.BooleanField(default=False) #new
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
    #NAM3
    unit = models.ForeignKey('Unit', null=True, blank=True, on_delete=models.SET_NULL)

    def is_unit_approver(self):
        return self.role == 'unitapprover'

    def is_clerk(self):
        return self.role == 'clerk'

    def is_auditor(self):
        return self.role == 'auditor'

    def can_approve(self, req=None):
        if self.is_superuser or self.is_org_approver or self.role == 'admin':
            return True
        if self.role == 'unitapprover' and req:
            return self.unit == req.unit
        return False

    def can_submit_requests(self):
        return self.role in ['basicuser', 'clerk']

    # CustomUser.is_unit_approver = is_unit_approver
    # CustomUser.is_clerk = is_clerk
    # CustomUser.is_auditor = is_auditor
    # CustomUser.can_approve = can_approve
    # CustomUser.can_submit_requests = can_submit_requests
    


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
    
    #New
    unit = models.ForeignKey('Unit', null=True, blank=True, on_delete=models.SET_NULL)
    
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




# Reduced Course Load Form
class RCLResponses(models.Model):  # FOR INTEGRATION
    user_name = models.CharField(max_length=100, null=True, blank=True)

    request_type = models.CharField(max_length=100, blank=True, null=True)

    student_name = models.CharField(max_length=100, blank=True, null=True)
    ps_id = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    student_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    initial_adjustment_issues = models.BooleanField(default=False)
    initial_adjustment_explanation = models.TextField(blank=True, null=True)

    improper_course_level_placement = models.BooleanField(default=False)
    iclp_class1 = models.CharField(max_length=50, blank=True, null=True)
    iclp_professor1 = models.CharField(max_length=100, blank=True, null=True)
    iclp_professor_signature1 = models.ImageField(upload_to='signatures/', blank=True, null=True)
    iclp_date1 = models.DateTimeField(blank=True, null=True)

    iclp_class2 = models.CharField(max_length=50, blank=True, null=True)
    iclp_professor2 = models.CharField(max_length=100, blank=True, null=True)
    iclp_professor_signature2 = models.ImageField(upload_to='signatures/', blank=True, null=True)
    iclp_date2 = models.DateTimeField(blank=True, null=True)

    medical_reason = models.BooleanField(default=False)
    medical_letter_attached = models.BooleanField(default=False)

    final_semester = models.BooleanField(default=False)
    final_semester_hours_needed = models.IntegerField(blank=True, null=True)

    concurrent_enrollment = models.BooleanField(default=False)
    concurrent_university_name = models.CharField(max_length=100, blank=True, null=True)
    concurrent_hours_uh = models.IntegerField(blank=True, null=True)
    concurrent_hours_other = models.IntegerField(blank=True, null=True)

    semester_fall = models.BooleanField(default=False)
    semester_spring = models.BooleanField(default=False)
    year_last_digit = models.IntegerField(blank=True, null=True)
    drop_courses = models.CharField(max_length=255, blank=True, null=True)
    remaining_hours_uh = models.IntegerField(blank=True, null=True)

    advisor_name = models.CharField(max_length=100, blank=True, null=True)
    advisor_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    advisor_date = models.DateTimeField(blank=True, null=True)

    isss_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    isss_date = models.DateTimeField(blank=True, null=True)

    is_finalized = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

# RCL Supporting Documents
class RCLDocuments(models.Model):
    response_id = models.IntegerField(null=True, blank=True)

    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.FileField(upload_to='rcl_documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name}"

# Term Withdrawal Form
class TWResponses(models.Model):  # FOR INTEGRATION
    user_name = models.CharField(max_length=100, null=True, blank=True)

    request_type = models.CharField(max_length=100, blank=True, null=True)

    student_name = models.CharField(max_length=100, blank=True, null=True)
    ps_id = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    academic_career = models.CharField(max_length=100, blank=True, null=True)
    student_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    withdrawal_term_fall = models.BooleanField(default=False)
    withdrawal_term_spring = models.BooleanField(default=False)
    withdrawal_term_summer = models.BooleanField(default=False)
    withdrawal_year = models.IntegerField(blank=True, null=True)

    financial_aid_ack = models.BooleanField(default=False)
    international_students_ack = models.BooleanField(default=False)
    student_athlete_ack = models.BooleanField(default=False)
    veterans_ack = models.BooleanField(default=False)
    graduate_students_ack = models.BooleanField(default=False)
    doctoral_students_ack = models.BooleanField(default=False)
    housing_ack = models.BooleanField(default=False)
    dining_ack = models.BooleanField(default=False)
    parking_ack = models.BooleanField(default=False)

    supporting_documents_attached = models.BooleanField(default=False)
    supporting_document_path = models.FileField(upload_to='tw_documents/', blank=True, null=True)

    is_finalized = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

# TW Supporting Documents
class TWDocuments(models.Model):
    response_id = models.IntegerField(null=True, blank=True)

    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.FileField(upload_to='tw_documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name}"

#NAM3 Define the organization as a hierarchy of units
class Unit(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='sub_units', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

#NAM3 Allow approvers to delegate approval responsibilities
class Delegation(models.Model):
    delegator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='delegated_by')
    delegate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='delegate_for')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.delegator} → {self.delegate} ({self.start_date} to {self.end_date})"
