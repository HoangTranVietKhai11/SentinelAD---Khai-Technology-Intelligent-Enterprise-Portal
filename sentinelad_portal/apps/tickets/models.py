from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('critical', 'Khẩn cấp'),
    ]
    STATUS_CHOICES = [
        ('open', 'Mở'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
        ('closed', 'Đóng'),
    ]

    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    description = models.TextField(verbose_name='Mô tả vấn đề')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Mức ưu tiên')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open', verbose_name='Trạng thái')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_created',
                                   verbose_name='Người tạo')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='tickets_assigned', verbose_name='Người xử lý')
    resolution = models.TextField(blank=True, verbose_name='Cách giải quyết')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Ticket Hỗ trợ'
        verbose_name_plural = 'Tickets Hỗ trợ'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.pk} - {self.title}"


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Nội dung')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.ticket}"
