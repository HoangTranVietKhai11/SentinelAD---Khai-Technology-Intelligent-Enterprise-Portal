from django.db import models
from django.contrib.auth.models import User


class Announcement(models.Model):
    LEVEL_CHOICES = [
        ('normal', 'Thông thường'),
        ('important', 'Quan trọng'),
        ('urgent', 'Khẩn cấp'),
    ]
    CATEGORY_CHOICES = [
        ('general', 'Chung'),
        ('new_employee', 'Nhân viên mới'),
        ('company_update', 'Cập nhật công ty'),
        ('event', 'Sự kiện'),
        ('policy', 'Chính sách'),
    ]

    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    content = models.TextField(verbose_name='Nội dung')
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='normal', verbose_name='Mức độ')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', verbose_name='Danh mục')
    pinned = models.BooleanField(default=False, verbose_name='Ghim lên đầu')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người đăng')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'
        ordering = ['-pinned', '-created_at']

    def __str__(self):
        return self.title
