#!/usr/bin/env python
"""
Khai Technology - Intranet Portal - Seed Data Script
Khởi tạo dữ liệu mẫu: Users, Departments, Employees, Assets, Tickets, Announcements, Meetings, Payroll
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinelad_portal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from apps.employees.models import Department, Employee
from apps.assets.models import Asset
from apps.tickets.models import Ticket, TicketComment
from apps.announcements.models import Announcement
from apps.audit.models import AuditLog
from apps.meetings.models import Meeting, MeetingAttendee
from apps.payroll.models import PayrollNotification
from datetime import date, timedelta
from django.utils import timezone

print("🌱 Seeding Khai Technology Intranet Portal data...")

# ── Users (mock AD accounts from khai.local) ─────────────────────────────────
users_data = [
    {'username': 'khai.it', 'first_name': 'Khai', 'last_name': 'IT Admin',
     'email': 'khai.it@khai.local', 'is_superuser': True, 'is_staff': True,
     'role': 'administrator', 'dept': 'IT', 'title': 'IT Administrator'},
    {'username': 'an.hr', 'first_name': 'An', 'last_name': 'HR',
     'email': 'an.hr@khai.local', 'role': 'hr_manager', 'dept': 'HR', 'title': 'HR Manager'},
    {'username': 'minh.finance', 'first_name': 'Minh', 'last_name': 'Finance',
     'email': 'minh.finance@khai.local', 'role': 'finance_manager', 'dept': 'Finance', 'title': 'Finance Manager'},
    {'username': 'hung.sales', 'first_name': 'Hung', 'last_name': 'Sales',
     'email': 'hung.sales@khai.local', 'role': 'sales_manager', 'dept': 'Sales', 'title': 'Sales Manager'},
    {'username': 'duc.helpdesk', 'first_name': 'Duc', 'last_name': 'Helpdesk',
     'email': 'duc.helpdesk@khai.local', 'role': 'helpdesk', 'dept': 'IT', 'title': 'IT Helpdesk'},
]

created_users = {}
for ud in users_data:
    user, created = User.objects.get_or_create(username=ud['username'])
    user.first_name = ud['first_name']
    user.last_name = ud['last_name']
    user.email = ud['email']
    user.is_superuser = ud.get('is_superuser', False)
    user.is_staff = ud.get('is_staff', False)
    user.set_password('Admin@123456')
    user.save()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = ud['role']
    profile.department = ud['dept']
    profile.title = ud['title']
    profile.save()
    created_users[ud['username']] = user
    print(f"  ✅ User: {ud['username']} ({ud['role']})")

# ── Departments ───────────────────────────────────────────────────────────────
depts_data = [
    ('IT', 'Phòng Công nghệ Thông tin', 'Khai IT Admin'),
    ('HR', 'Phòng Nhân sự', 'An HR'),
    ('Finance', 'Phòng Tài chính - Kế toán', 'Minh Finance'),
    ('Sales', 'Phòng Kinh doanh - Bán hàng', 'Hung Sales'),
    ('Marketing', 'Phòng Marketing', ''),
    ('Management', 'Ban Giám đốc', ''),
]

depts = {}
for name, desc, mgr in depts_data:
    dept, _ = Department.objects.get_or_create(name=name, defaults={'description': desc, 'manager_name': mgr})
    depts[name] = dept
    print(f"  🏢 Dept: {name}")

# ── Employees ─────────────────────────────────────────────────────────────────
employees_data = [
    ('NV001', 'Nguyễn Văn Khai', 'khai.it@khai.local', 'IT', 'IT Administrator', '0901234567', date(2022, 1, 15), 'active'),
    ('NV002', 'Trần Thị An', 'an.hr@khai.local', 'HR', 'HR Manager', '0902345678', date(2021, 6, 1), 'active'),
    ('NV003', 'Lê Văn Minh', 'minh.finance@khai.local', 'Finance', 'Finance Manager', '0903456789', date(2020, 3, 10), 'active'),
    ('NV004', 'Phạm Văn Hùng', 'hung.sales@khai.local', 'Sales', 'Sales Manager', '0904567890', date(2021, 9, 5), 'active'),
    ('NV005', 'Nguyễn Đức', 'duc.helpdesk@khai.local', 'IT', 'IT Helpdesk', '0905678901', date(2023, 2, 20), 'active'),
    ('NV006', 'Võ Thị Lan', 'lan.marketing@khai.local', 'Marketing', 'Marketing Specialist', '0906789012', date(2022, 8, 15), 'active'),
    ('NV007', 'Đỗ Minh Tuấn', 'tuan.sales@khai.local', 'Sales', 'Sales Representative', '0907890123', date(2023, 5, 1), 'active'),
    ('NV008', 'Lý Thị Hoa', 'hoa.hr@khai.local', 'HR', 'HR Specialist', '0908901234', date(2022, 11, 1), 'active'),
    # New employees (hired recently)
    ('NV009', 'Trương Minh Đạt', 'dat.dev@khai.local', 'IT', 'Full-Stack Developer', '0909012345', date(2026, 8, 15), 'active'),
    ('NV010', 'Nguyễn Thị Mai', 'mai.design@khai.local', 'Marketing', 'UI/UX Designer', '0910123456', date(2026, 8, 20), 'active'),
]

for emp_id, name, email, dept_name, pos, phone, hire, status in employees_data:
    emp, _ = Employee.objects.get_or_create(employee_id=emp_id, defaults={
        'full_name': name, 'email': email, 'department': depts.get(dept_name),
        'position': pos, 'phone': phone, 'hire_date': hire, 'status': status,
    })
    print(f"  👤 Employee: {name}")

# ── Assets ────────────────────────────────────────────────────────────────────
assets_data = [
    ('ASSET-001', 'Dell Latitude 5540', 'laptop', 'SN-DELL-001', 'Nguyễn Văn Khai', date(2023, 1, 15), date(2026, 1, 15), 'in_use'),
    ('ASSET-002', 'Dell PowerEdge R750 (DC-01)', 'server', 'SN-DELL-SRV-001', 'DC-01 Room', date(2022, 6, 1), date(2027, 6, 1), 'in_use'),
    ('ASSET-003', 'HP ProBook 450 G10', 'laptop', 'SN-HP-002', 'Trần Thị An', date(2023, 3, 10), date(2026, 3, 10), 'in_use'),
    ('ASSET-004', 'Cisco Catalyst 2960-X', 'switch', 'SN-CISCO-001', 'Server Room', date(2021, 5, 20), date(2024, 5, 20), 'in_use'),
    ('ASSET-005', 'Fortinet FortiGate 60F', 'firewall', 'SN-FORTI-001', 'Server Room', date(2022, 1, 10), date(2025, 1, 10), 'in_use'),
    ('ASSET-006', 'Lenovo ThinkPad E15', 'laptop', 'SN-LEN-001', 'Lê Văn Minh', date(2023, 7, 1), date(2026, 7, 1), 'in_use'),
    ('ASSET-007', 'HP LaserJet Pro M404n', 'printer', 'SN-HP-PRT-001', 'HR Department', date(2021, 9, 15), date(2024, 9, 15), 'in_use'),
    ('ASSET-008', 'Dell OptiPlex 7010', 'desktop', 'SN-DELL-DT-001', '', date(2022, 12, 1), date(2025, 12, 1), 'in_stock'),
    ('ASSET-009', 'Dell PowerEdge R640 (WEB01)', 'server', 'SN-DELL-SRV-002', 'WEB01 Room', date(2023, 1, 1), date(2028, 1, 1), 'in_use'),
    ('ASSET-010', 'Cisco Router ISR4221', 'router', 'SN-CISCO-RTR-001', 'Server Room', date(2021, 3, 1), date(2024, 3, 1), 'in_use'),
]

for tag, name, atype, serial, user_name, pd, wd, status in assets_data:
    Asset.objects.get_or_create(asset_tag=tag, defaults={
        'asset_name': name, 'asset_type': atype, 'serial_number': serial,
        'assigned_user_name': user_name, 'purchase_date': pd, 'warranty_date': wd, 'status': status,
    })
    print(f"  🖥️  Asset: {name}")

# ── Tickets ───────────────────────────────────────────────────────────────────
admin_user = created_users.get('khai.it')
helpdesk_user = created_users.get('duc.helpdesk')
an_user = created_users.get('an.hr')

tickets_data = [
    ('Không kết nối được mạng nội bộ', 'Máy tính tại phòng HR không thể kết nối vào mạng khai.local từ sáng nay. IP tĩnh đã được cấu hình nhưng không ping được DC-01.', 'high', 'open', an_user, helpdesk_user),
    ('Yêu cầu cấp quyền truy cập phần mềm kế toán', 'Nhân viên mới cần được cấp quyền truy cập hệ thống kế toán nội bộ theo chính sách RBAC.', 'medium', 'in_progress', an_user, admin_user),
    ('Máy in phòng HR bị kẹt giấy thường xuyên', 'HP LaserJet Pro M404n (ASSET-007) bị kẹt giấy liên tục. Đã thử vệ sinh nhưng vẫn tái diễn.', 'low', 'resolved', an_user, helpdesk_user),
    ('VPN không kết nối được từ remote', 'Không thể kết nối VPN về hệ thống khai.local khi làm việc từ xa. Lỗi xảy ra sau khi đổi mật khẩu.', 'critical', 'open', admin_user, None),
    ('Yêu cầu cài đặt phần mềm mới', 'Cần cài đặt Microsoft Visio 2021 cho phòng IT để vẽ sơ đồ hạ tầng mạng.', 'low', 'closed', admin_user, helpdesk_user),
]

for title, desc, priority, status, creator, assignee in tickets_data:
    ticket, created = Ticket.objects.get_or_create(title=title, defaults={
        'description': desc, 'priority': priority, 'status': status,
        'created_by': creator, 'assigned_to': assignee,
    })
    if created:
        if status in ('resolved', 'closed'):
            ticket.resolved_at = timezone.now() - timedelta(days=1)
            ticket.resolution = 'Đã kiểm tra và xử lý vấn đề thành công.'
            ticket.save()
    print(f"  🎫 Ticket: {title[:45]}")

# ── Announcements (with categories) ──────────────────────────────────────────
ann_data = [
    ('Cập nhật chính sách bảo mật mật khẩu', 'Theo yêu cầu bảo mật, tất cả nhân viên cần đổi mật khẩu trong vòng 7 ngày tới. Mật khẩu mới phải có tối thiểu 12 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt.', 'urgent', 'policy', True, admin_user),
    ('Khai Technology ra mắt Cổng Thông tin Nội bộ mới', 'Hệ thống Cổng thông tin nội bộ Khai Technology đã được triển khai thành công. Truy cập tại http://intranet.khai.local để sử dụng các tính năng mới: Lịch họp, Thông báo lương, Quản lý Ticket và nhiều hơn nữa.', 'important', 'company_update', True, admin_user),
    ('Lịch bảo trì máy chủ định kỳ tháng 9/2026', 'Máy chủ DC-01 (192.168.101.10) sẽ được bảo trì vào ngày 15/09/2026 từ 22:00 - 02:00. Dịch vụ AD, DNS, DHCP sẽ tạm ngưng trong thời gian này.', 'important', 'company_update', False, admin_user),
    ('Chào mừng Trương Minh Đạt gia nhập phòng IT', 'Kính chào mừng anh Trương Minh Đạt - Full-Stack Developer mới gia nhập phòng Công nghệ Thông tin từ ngày 15/08/2026. Anh Đạt sẽ phụ trách phát triển các ứng dụng web nội bộ. Hãy cùng chào đón anh ấy nhé! 🎉', 'normal', 'new_employee', False, an_user),
    ('Chào mừng Nguyễn Thị Mai gia nhập phòng Marketing', 'Kính chào mừng chị Nguyễn Thị Mai - UI/UX Designer mới gia nhập phòng Marketing từ ngày 20/08/2026. Chị Mai sẽ phụ trách thiết kế giao diện sản phẩm. Chúc chị Mai nhiều thành công! 🎉', 'normal', 'new_employee', False, an_user),
    ('Team Building Q3/2026 - Đà Lạt', 'Khai Technology tổ chức chương trình Team Building Q3/2026 tại Đà Lạt từ ngày 20-22/09/2026. Nhân viên đăng ký tham gia trước ngày 10/09/2026. Chi phí do công ty tài trợ toàn bộ.', 'important', 'event', False, an_user),
]

for title, content, level, category, pinned, creator in ann_data:
    Announcement.objects.get_or_create(title=title, defaults={
        'content': content, 'level': level, 'category': category,
        'pinned': pinned, 'created_by': creator,
    })
    print(f"  📢 Announcement: {title[:50]}")

# ── Meetings ──────────────────────────────────────────────────────────────────
now = timezone.now()
meetings_data = [
    ('Daily Standup - Phòng IT', 'Cập nhật tiến độ công việc hàng ngày.', 'standup', 'Google Meet',
     now.replace(hour=9, minute=0, second=0), now.replace(hour=9, minute=15, second=0),
     admin_user, 'normal', True),
    ('Họp Sprint Review Q3 - Sprint 6', 'Review kết quả Sprint 6: Portal nội bộ, tích hợp AI Analysis, Grafana Dashboard.', 'review', 'Phòng họp A',
     now.replace(hour=14, minute=0, second=0), now.replace(hour=15, minute=30, second=0),
     admin_user, 'important', False),
    ('All Hands Meeting tháng 9/2026', 'Cập nhật tình hình công ty, kế hoạch Q4, chào đón nhân viên mới.', 'all_hands', 'Phòng họp lớn',
     (now + timedelta(days=1)).replace(hour=10, minute=0, second=0), (now + timedelta(days=1)).replace(hour=11, minute=30, second=0),
     admin_user, 'important', False),
    ('Họp Team Sales - Chiến lược tháng 9', 'Thảo luận chiến lược bán hàng và mục tiêu doanh thu tháng 9/2026.', 'team', 'Phòng họp B',
     (now + timedelta(days=2)).replace(hour=9, minute=30, second=0), (now + timedelta(days=2)).replace(hour=10, minute=30, second=0),
     created_users.get('hung.sales'), 'normal', False),
    ('Đào tạo an ninh mạng cho nhân viên mới', 'Hướng dẫn chính sách bảo mật, sử dụng VPN, Active Directory, và quy trình báo cáo sự cố bảo mật.', 'training', 'Zoom Meeting',
     (now + timedelta(days=3)).replace(hour=14, minute=0, second=0), (now + timedelta(days=3)).replace(hour=16, minute=0, second=0),
     admin_user, 'normal', False),
    ('Họp với khách hàng ABC Corp', 'Demo sản phẩm mới cho khách hàng ABC Corp. Chuẩn bị slide và demo live.', 'client', 'Google Meet',
     (now + timedelta(days=4)).replace(hour=10, minute=0, second=0), (now + timedelta(days=4)).replace(hour=11, minute=0, second=0),
     created_users.get('hung.sales'), 'important', False),
]

all_users_list = list(created_users.values())
for title, desc, mtype, location, start, end, organizer, priority, recurring in meetings_data:
    meeting, created = Meeting.objects.get_or_create(title=title, defaults={
        'description': desc, 'meeting_type': mtype, 'location': location,
        'start_time': start, 'end_time': end, 'organizer': organizer,
        'priority': priority, 'is_recurring': recurring,
    })
    if created:
        # Add all users as attendees
        for u in all_users_list:
            if u != organizer:
                MeetingAttendee.objects.get_or_create(meeting=meeting, user=u, defaults={'status': 'pending'})
    print(f"  📅 Meeting: {title[:50]}")

# ── Payroll Notifications ─────────────────────────────────────────────────────
payroll_data = [
    ('khai.it', 'Tháng 8/2026', 25000000, 3000000, 2000000, 3150000),
    ('an.hr', 'Tháng 8/2026', 20000000, 2000000, 1000000, 2530000),
    ('minh.finance', 'Tháng 8/2026', 22000000, 2500000, 1500000, 2860000),
    ('hung.sales', 'Tháng 8/2026', 18000000, 2000000, 5000000, 2750000),
    ('duc.helpdesk', 'Tháng 8/2026', 15000000, 1500000, 500000, 1870000),
]

for username, period, base, allowance, bonus, deduction in payroll_data:
    emp_user = created_users.get(username)
    if emp_user:
        net = base + allowance + bonus - deduction
        PayrollNotification.objects.get_or_create(
            employee=emp_user, period=period,
            defaults={
                'base_salary': base, 'allowance': allowance, 'bonus': bonus,
                'deduction': deduction, 'net_salary': net,
                'note': 'Lương tháng 8/2026 - Khai Technology',
                'status': 'sent', 'created_by': admin_user,
                'sent_at': timezone.now(),
            }
        )
        print(f"  💰 Payroll: {username} - {period} - Net: {net:,.0f}đ")

# ── Audit Logs ────────────────────────────────────────────────────────────────
AuditLog.objects.get_or_create(
    username='khai.it', action='LOGIN_SUCCESS', resource_type='',
    defaults={'user': admin_user, 'description': 'Login via Mock AD', 'source_ip': '192.168.101.10'}
)

print("\n✅ Seed data completed successfully!")
print("=" * 55)
print(f"  👥 Users          : {User.objects.count()}")
print(f"  🏢 Departments    : {Department.objects.count()}")
print(f"  👤 Employees      : {Employee.objects.count()}")
print(f"  🖥️  Assets         : {Asset.objects.count()}")
print(f"  🎫 Tickets        : {Ticket.objects.count()}")
print(f"  📢 Announcements  : {Announcement.objects.count()}")
print(f"  📅 Meetings       : {Meeting.objects.count()}")
print(f"  💰 Payroll        : {PayrollNotification.objects.count()}")
print("=" * 55)
print("  🌐 Start server: python manage.py runserver 0.0.0.0:80")
print("  🔐 Login with : khai.it / Admin@123456")
print("  🏢 Company    : Khai Technology")
