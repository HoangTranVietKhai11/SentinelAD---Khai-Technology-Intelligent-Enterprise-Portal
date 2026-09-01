from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.employees.models import Employee, Department
from apps.assets.models import Asset
from apps.tickets.models import Ticket
from apps.announcements.models import Announcement
from apps.audit.models import AuditLog
from apps.meetings.models import Meeting, MeetingAttendee
from apps.payroll.models import PayrollNotification
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard(request):
    today = timezone.now()
    last_30_days = today - timedelta(days=30)

    # Stats
    total_employees = Employee.objects.filter(status='active').count()
    total_departments = Department.objects.count()
    total_assets = Asset.objects.count()
    open_tickets = Ticket.objects.filter(status__in=['open', 'in_progress']).count()
    resolved_tickets = Ticket.objects.filter(status__in=['resolved', 'closed']).count()

    # Asset by type for chart
    asset_types = {}
    for choice_key, choice_label in Asset.TYPE_CHOICES:
        count = Asset.objects.filter(asset_type=choice_key).count()
        if count > 0:
            asset_types[choice_label] = count

    # Ticket by priority for chart
    ticket_priorities = {}
    for pk, pl in Ticket.PRIORITY_CHOICES:
        count = Ticket.objects.filter(priority=pk, status__in=['open', 'in_progress']).count()
        ticket_priorities[pl] = count

    # Recent audit logs
    recent_logs = AuditLog.objects.select_related('user')[:10]

    # All announcements (pinned first)
    announcements = Announcement.objects.filter(is_active=True)[:5]

    # Pinned announcements
    pinned_announcements = Announcement.objects.filter(is_active=True, pinned=True)[:3]

    # Expiring warranties
    expiring_assets = Asset.objects.filter(
        warranty_date__lte=today.date() + timedelta(days=30),
        warranty_date__gte=today.date(),
        status='in_use'
    )[:5]

    # ── New features for Khai Technology portal ──

    # Upcoming meetings (today + tomorrow)
    tomorrow = today + timedelta(days=1)
    upcoming_meetings = Meeting.objects.filter(
        start_time__date__gte=today.date(),
        start_time__date__lte=tomorrow.date()
    ).select_related('organizer')[:5]

    # This week's meetings
    week_end = today + timedelta(days=7)
    week_meetings = Meeting.objects.filter(
        start_time__gte=today,
        start_time__lte=week_end
    ).select_related('organizer')

    # New employees (hired in last 30 days)
    new_employees = Employee.objects.filter(
        hire_date__gte=(today - timedelta(days=30)).date(),
        status='active'
    ).select_related('department')[:6]

    # New employee announcements
    new_employee_announcements = Announcement.objects.filter(
        is_active=True, category='new_employee'
    )[:3]

    # Latest payroll for current user
    latest_payroll = PayrollNotification.objects.filter(
        employee=request.user, status='sent'
    ).first()

    # Unread payroll count
    unread_payroll = PayrollNotification.objects.filter(
        employee=request.user, status='sent', is_read=False
    ).count()

    context = {
        'page_title': 'Trang chủ - Khai Technology',
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_assets': total_assets,
        'open_tickets': open_tickets,
        'resolved_tickets': resolved_tickets,
        'asset_types': asset_types,
        'ticket_priorities': ticket_priorities,
        'recent_logs': recent_logs,
        'announcements': announcements,
        'pinned_announcements': pinned_announcements,
        'expiring_assets': expiring_assets,
        'upcoming_meetings': upcoming_meetings,
        'week_meetings': week_meetings,
        'new_employees': new_employees,
        'new_employee_announcements': new_employee_announcements,
        'latest_payroll': latest_payroll,
        'unread_payroll': unread_payroll,
        'current_time': today,
    }
    return render(request, 'core/dashboard.html', context)
