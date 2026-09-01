from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('administrator', 'Administrator'),
    ('helpdesk', 'IT Helpdesk'),
    ('hr_manager', 'HR Manager'),
    ('finance_manager', 'Finance Manager'),
    ('sales_manager', 'Sales Manager'),
    ('employee', 'Employee'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    ad_groups = models.TextField(blank=True, help_text='Comma-separated AD group names')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_administrator(self):
        return self.role == 'administrator'

    @property
    def is_helpdesk(self):
        return self.role in ('administrator', 'helpdesk')

    @property
    def is_hr_manager(self):
        return self.role in ('administrator', 'hr_manager')

    @property
    def is_manager(self):
        return self.role in ('administrator', 'hr_manager', 'finance_manager', 'sales_manager')
