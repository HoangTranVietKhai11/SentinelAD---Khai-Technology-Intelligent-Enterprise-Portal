from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Employee, Department
from apps.audit.middleware import log_action
from apps.authentication.ad_provisioning import create_ad_ou, create_ad_user, disable_ad_user

from django.core.management import call_command

def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.is_administrator

admin_required = user_passes_test(is_admin, login_url='/dashboard/', redirect_field_name=None)


@login_required
@admin_required
def sync_ad_view(request):
    try:
        call_command('sync_ad')
        messages.success(request, 'Đã đồng bộ 100% dữ liệu từ máy chủ Active Directory (DC-01) thành công!')
    except Exception as e:
        messages.error(request, f'Lỗi khi đồng bộ từ DC-01: {e}')
    
    referrer = request.META.get('HTTP_REFERER')
    if referrer and 'departments' in referrer:
        return redirect('department_list')
    return redirect('employee_list')


# ─── DEPARTMENTS ─────────────────────────────────────────────────────────────
@login_required
def department_list(request):
    depts = Department.objects.all()
    return render(request, 'employees/department_list.html', {
        'page_title': 'Quản lý Phòng ban',
        'departments': depts,
    })


@login_required
@admin_required
def department_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        manager_name = request.POST.get('manager_name', '').strip()
        if name:
            dept = Department.objects.create(name=name, description=description, manager_name=manager_name)
            log_action(request.user, 'CREATE', 'Department', dept.pk, dept.name,
                       f'Created department: {dept.name}', request.META.get('REMOTE_ADDR'))
            
            # Sync to Active Directory
            ad_ok, ad_msg = create_ad_ou(dept.name)
            if ad_ok:
                messages.success(request, f'Đã tạo phòng ban "{name}" thành công và đồng bộ AD.')
            else:
                messages.warning(request, f'Đã tạo phòng ban "{name}" trên Web, nhưng lỗi AD: {ad_msg}')
                
            return redirect('department_list')
        messages.error(request, 'Tên phòng ban không được để trống.')
    return render(request, 'employees/department_form.html', {'page_title': 'Thêm Phòng ban'})


@login_required
@admin_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.name = request.POST.get('name', dept.name).strip()
        dept.description = request.POST.get('description', '').strip()
        dept.manager_name = request.POST.get('manager_name', '').strip()
        dept.save()
        log_action(request.user, 'UPDATE', 'Department', dept.pk, dept.name,
                   f'Updated department: {dept.name}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Đã cập nhật phòng ban "{dept.name}".')
        return redirect('department_list')
    return render(request, 'employees/department_form.html', {'page_title': 'Sửa Phòng ban', 'dept': dept})


@login_required
@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = dept.name
        dept.delete()
        log_action(request.user, 'DELETE', 'Department', pk, name,
                   f'Deleted department: {name}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Đã xóa phòng ban "{name}".')
        return redirect('department_list')
    return render(request, 'employees/department_confirm_delete.html', {'dept': dept})


# ─── EMPLOYEES ────────────────────────────────────────────────────────────────
@login_required
def employee_list(request):
    query = request.GET.get('q', '')
    dept_filter = request.GET.get('dept', '')
    status_filter = request.GET.get('status', '')
    employees = Employee.objects.select_related('department').all()
    if query:
        employees = employees.filter(
            Q(full_name__icontains=query) | Q(employee_id__icontains=query) |
            Q(email__icontains=query) | Q(position__icontains=query)
        )
    if dept_filter:
        employees = employees.filter(department_id=dept_filter)
    if status_filter:
        employees = employees.filter(status=status_filter)
    return render(request, 'employees/employee_list.html', {
        'page_title': 'Quản lý Nhân viên',
        'employees': employees,
        'departments': Department.objects.all(),
        'query': query,
        'dept_filter': dept_filter,
        'status_filter': status_filter,
    })


@login_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'page_title': emp.full_name, 'emp': emp})


@login_required
@admin_required
def employee_create(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        emp = Employee(
            employee_id=request.POST.get('employee_id', ''),
            full_name=request.POST.get('full_name', ''),
            email=request.POST.get('email', ''),
            position=request.POST.get('position', ''),
            phone=request.POST.get('phone', ''),
            status=request.POST.get('status', 'active'),
        )
        dept_id = request.POST.get('department')
        if dept_id:
            emp.department_id = dept_id
        hire_date = request.POST.get('hire_date')
        if hire_date:
            emp.hire_date = hire_date
        try:
            emp.save()
            log_action(request.user, 'CREATE', 'Employee', emp.pk, emp.full_name,
                       f'Created employee: {emp.full_name}', request.META.get('REMOTE_ADDR'))
                       
            # Sync to Active Directory
            username = emp.email.split('@')[0] if '@' in emp.email else emp.employee_id
            name_parts = emp.full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            dept_name = emp.department.name if emp.department else 'Company'
            
            ad_ok, ad_msg = create_ad_user(username, first_name, last_name, emp.full_name, emp.email, dept_name)
            if ad_ok:
                messages.success(request, f'Đã thêm nhân viên "{emp.full_name}" và đồng bộ AD thành công.')
            else:
                messages.warning(request, f'Thêm nhân viên "{emp.full_name}" trên Web thành công, nhưng lỗi AD: {ad_msg}')
                
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
    return render(request, 'employees/employee_form.html', {'page_title': 'Thêm Nhân viên', 'departments': departments})


@login_required
@admin_required
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    departments = Department.objects.all()
    if request.method == 'POST':
        emp.full_name = request.POST.get('full_name', emp.full_name)
        emp.email = request.POST.get('email', emp.email)
        emp.position = request.POST.get('position', '')
        emp.phone = request.POST.get('phone', '')
        emp.status = request.POST.get('status', 'active')
        dept_id = request.POST.get('department')
        emp.department_id = dept_id if dept_id else None
        hire_date = request.POST.get('hire_date')
        emp.hire_date = hire_date if hire_date else None
        try:
            emp.save()
            log_action(request.user, 'UPDATE', 'Employee', emp.pk, emp.full_name,
                       f'Updated employee: {emp.full_name}', request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Đã cập nhật nhân viên "{emp.full_name}".')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
    return render(request, 'employees/employee_form.html', {
        'page_title': 'Sửa Nhân viên', 'emp': emp, 'departments': departments
    })


@login_required
@admin_required
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = emp.full_name
        username = emp.email.split('@')[0] if '@' in emp.email else emp.employee_id
        emp.delete()
        log_action(request.user, 'DELETE', 'Employee', pk, name,
                   f'Deleted employee: {name}', request.META.get('REMOTE_ADDR'))
                   
        # Disable in Active Directory
        ad_ok, ad_msg = disable_ad_user(username)
        if ad_ok:
            messages.success(request, f'Đã xóa nhân viên "{name}" và Disable AD User thành công.')
        else:
            messages.warning(request, f'Đã xóa nhân viên "{name}" trên Web, nhưng cảnh báo AD: {ad_msg}')
            
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'emp': emp})
