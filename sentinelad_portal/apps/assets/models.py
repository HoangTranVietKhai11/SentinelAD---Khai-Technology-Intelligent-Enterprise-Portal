from django.db import models
from django.contrib.auth.models import User


class Asset(models.Model):
    TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('printer', 'Máy in'),
        ('switch', 'Switch'),
        ('router', 'Router'),
        ('firewall', 'Firewall'),
        ('server', 'Server'),
        ('other', 'Khác'),
    ]
    STATUS_CHOICES = [
        ('in_use', 'Đang sử dụng'),
        ('in_stock', 'Trong kho'),
        ('repair', 'Đang sửa chữa'),
        ('retired', 'Đã thanh lý'),
    ]

    asset_tag = models.CharField(max_length=50, unique=True, verbose_name='Mã tài sản')
    asset_name = models.CharField(max_length=200, verbose_name='Tên thiết bị')
    asset_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Loại thiết bị')
    serial_number = models.CharField(max_length=100, blank=True, verbose_name='Số Serial')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assets', verbose_name='Người sử dụng')
    assigned_user_name = models.CharField(max_length=150, blank=True, verbose_name='Tên người sử dụng')
    purchase_date = models.DateField(null=True, blank=True, verbose_name='Ngày mua')
    warranty_date = models.DateField(null=True, blank=True, verbose_name='Hết hạn bảo hành')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock', verbose_name='Trạng thái')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tài sản CNTT'
        verbose_name_plural = 'Tài sản CNTT'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.asset_tag}] {self.asset_name}"

    @property
    def is_warranty_expiring(self):
        from datetime import date, timedelta
        if self.warranty_date:
            return self.warranty_date <= date.today() + timedelta(days=30)
        return False
