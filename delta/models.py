from django.contrib.auth.models import AbstractUser
from django.db import models

class ApprovalStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending'
    RETURNED = 'returned', 'Returned'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('basicuser', 'Basic User'),
        ('admin', 'Administrator'),
        ('developer', 'Developer'),
        ('editor', 'Editor'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='basicuser')
    status = models.BooleanField(default=True)

    # Add related_name parameters to these fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='delta_customuser_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='delta_customuser_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username


class AcademicRequest(models.Model):
    # Change this to use a string reference to avoid circular imports
    requestor = models.ForeignKey('delta.CustomUser', on_delete=models.CASCADE)
    form_name = models.CharField(max_length=100)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.DRAFT
    )
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    document = models.FileField(upload_to='documents/', blank=True, null=True)

    def __str__(self):
        return f"{self.form_name} - {self.status}"