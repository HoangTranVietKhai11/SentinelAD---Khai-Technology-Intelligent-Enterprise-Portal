from django.db import models
from django.contrib.auth.models import User


class PayrollNotification(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('sent', 'Đã gửi'),
        ('confirmed', 'Đã xác nhận'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payroll_notifications',
                                 verbose_name='Nhân viên')
    period = models.CharField(max_length=50, verbose_name='Kỳ lương',
                              help_text='Ví dụ: Tháng 8/2026')
    base_salary = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Lương cơ bản')
    allowance = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Phụ cấp')
    bonus = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Thưởng')
    deduction = models.DecimalField(max_digits=15, decimal_places=0, default=0,
                                    verbose_name='Khấu trừ (BHXH, thuế...)')
    net_salary = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Thực lãnh')
    note = models.TextField(blank=True, verbose_name='Ghi chú')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft', verbose_name='Trạng thái')
    is_read = models.BooleanField(default=False, verbose_name='Đã xem')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payroll_created',
                                   verbose_name='Người tạo')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Ngày gửi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phiếu lương'
        verbose_name_plural = 'Phiếu lương'
        ordering = ['-created_at']
        unique_together = ['employee', 'period']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.period}"

    @property
    def total_income(self):
        return self.base_salary + self.allowance + self.bonus

    @property
    def formatted_net_salary(self):
        return f"{self.net_salary:,.0f}"
