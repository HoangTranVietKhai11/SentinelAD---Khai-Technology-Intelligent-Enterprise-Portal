from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên phòng ban')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    manager_name = models.CharField(max_length=150, blank=True, verbose_name='Trưởng phòng')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Phòng ban'
        verbose_name_plural = 'Phòng ban'
        ordering = ['name']

    def __str__(self):
        return self.name

    def employee_count(self):
        return self.employee_set.filter(status='active').count()


class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Đang làm việc'),
        ('inactive', 'Nghỉ việc'),
        ('onleave', 'Đang nghỉ phép'),
    ]

    employee_id = models.CharField(max_length=20, unique=True, verbose_name='Mã nhân viên')
    full_name = models.CharField(max_length=150, verbose_name='Họ và tên')
    email = models.EmailField(unique=True, verbose_name='Email')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name='Phòng ban')
    position = models.CharField(max_length=100, blank=True, verbose_name='Chức danh')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Số điện thoại')
    hire_date = models.DateField(null=True, blank=True, verbose_name='Ngày vào làm')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
