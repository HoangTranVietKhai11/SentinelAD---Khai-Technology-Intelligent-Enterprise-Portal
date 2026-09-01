from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import PayrollNotification


@login_required
def payroll_list(request):
    user_role = 'employee'
    try:
        user_role = request.user.userprofile.role
    except Exception:
        pass

    # Admin/HR see all, others see only their own
    if user_role in ('administrator', 'hr_manager'):
        payrolls = PayrollNotification.objects.select_related('employee', 'created_by').all()
    else:
        payrolls = PayrollNotification.objects.filter(
            employee=request.user, status='sent'
        ).select_related('employee', 'created_by')

    # Filter by period
    period_filter = request.GET.get('period', '')
    if period_filter:
        payrolls = payrolls.filter(period__icontains=period_filter)

    context = {
        'page_title': 'Thông báo lương - Khai Technology',
        'payrolls': payrolls,
        'user_role': user_role,
        'period_filter': period_filter,
    }
    return render(request, 'payroll/payroll_list.html', context)


@login_required
def payroll_create(request):
    # Only admin/HR can create
    user_role = 'employee'
    try:
        user_role = request.user.userprofile.role
    except Exception:
        pass

    if user_role not in ('administrator', 'hr_manager'):
        messages.error(request, 'Bạn không có quyền tạo phiếu lương.')
        return redirect('payroll_list')

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        period = request.POST.get('period', '').strip()
        base_salary = request.POST.get('base_salary', 0)
        allowance = request.POST.get('allowance', 0)
        bonus = request.POST.get('bonus', 0)
        deduction = request.POST.get('deduction', 0)
        net_salary = request.POST.get('net_salary', 0)
        note = request.POST.get('note', '').strip()
        status = request.POST.get('status', 'draft')

        try:
            employee = User.objects.get(pk=employee_id)
            payroll = PayrollNotification.objects.create(
                employee=employee,
                period=period,
                base_salary=int(base_salary) if base_salary else 0,
                allowance=int(allowance) if allowance else 0,
                bonus=int(bonus) if bonus else 0,
                deduction=int(deduction) if deduction else 0,
                net_salary=int(net_salary) if net_salary else 0,
                note=note,
                status=status,
                created_by=request.user,
                sent_at=timezone.now() if status == 'sent' else None,
            )
            messages.success(request, f'Đã tạo phiếu lương cho {employee.get_full_name()} ({period}).')
            return redirect('payroll_list')
        except User.DoesNotExist:
            messages.error(request, 'Nhân viên không tồn tại.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    users = User.objects.filter(is_active=True).order_by('first_name')
    context = {
        'page_title': 'Tạo phiếu lương',
        'users': users,
    }
    return render(request, 'payroll/payroll_form.html', context)


@login_required
def payroll_detail(request, pk):
    payroll = get_object_or_404(PayrollNotification, pk=pk)

    # Security: only owner or admin/HR can view
    user_role = 'employee'
    try:
        user_role = request.user.userprofile.role
    except Exception:
        pass

    if payroll.employee != request.user and user_role not in ('administrator', 'hr_manager'):
        messages.error(request, 'Bạn không có quyền xem phiếu lương này.')
        return redirect('payroll_list')

    # Mark as read
    if payroll.employee == request.user and not payroll.is_read:
        payroll.is_read = True
        payroll.save()

    context = {
        'page_title': f'Phiếu lương {payroll.period}',
        'payroll': payroll,
        'user_role': user_role,
    }
    return render(request, 'payroll/payroll_detail.html', context)
