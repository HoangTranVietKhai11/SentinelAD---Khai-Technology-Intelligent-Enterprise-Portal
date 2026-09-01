from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN_SUCCESS', 'Đăng nhập thành công'),
        ('LOGIN_FAILURE', 'Đăng nhập thất bại'),
        ('LOGOUT', 'Đăng xuất'),
        ('CREATE', 'Tạo mới'),
        ('UPDATE', 'Cập nhật'),
        ('DELETE', 'Xóa'),
        ('VIEW', 'Xem'),
        ('ASSIGN', 'Phân công'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, blank=True, verbose_name='Loại đối tượng')
    resource_id = models.CharField(max_length=50, blank=True, verbose_name='ID đối tượng')
    resource_name = models.CharField(max_length=200, blank=True, verbose_name='Tên đối tượng')
    description = models.TextField(blank=True, verbose_name='Chi tiết')
    source_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Địa chỉ IP')
    user_agent = models.CharField(max_length=300, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} | {self.username} | {self.action} | {self.resource_type}"
