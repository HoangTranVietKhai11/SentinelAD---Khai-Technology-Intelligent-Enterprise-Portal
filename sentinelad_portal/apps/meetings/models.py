from django.db import models
from django.contrib.auth.models import User


class Meeting(models.Model):
    TYPE_CHOICES = [
        ('standup', 'Daily Standup'),
        ('team', 'Họp Team'),
        ('all_hands', 'All Hands'),
        ('client', 'Họp với Khách hàng'),
        ('review', 'Sprint Review'),
        ('training', 'Đào tạo'),
        ('other', 'Khác'),
    ]
    PRIORITY_CHOICES = [
        ('normal', 'Bình thường'),
        ('important', 'Quan trọng'),
        ('urgent', 'Khẩn cấp'),
    ]

    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    description = models.TextField(blank=True, verbose_name='Mô tả / Nội dung')
    meeting_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='team', verbose_name='Loại cuộc họp')
    location = models.CharField(max_length=200, blank=True, verbose_name='Địa điểm',
                                help_text='Ví dụ: Phòng họp A, Google Meet, Zoom...')
    start_time = models.DateTimeField(verbose_name='Bắt đầu')
    end_time = models.DateTimeField(verbose_name='Kết thúc')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings',
                                  verbose_name='Người tổ chức')
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='normal', verbose_name='Mức độ')
    is_recurring = models.BooleanField(default=False, verbose_name='Lặp lại hàng tuần')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cuộc họp'
        verbose_name_plural = 'Cuộc họp'
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%d/%m %H:%M')})"

    @property
    def duration_minutes(self):
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)


class MeetingAttendee(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('accepted', 'Tham gia'),
        ('declined', 'Từ chối'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_invitations')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Người tham dự'
        verbose_name_plural = 'Người tham dự'
        unique_together = ['meeting', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}"
