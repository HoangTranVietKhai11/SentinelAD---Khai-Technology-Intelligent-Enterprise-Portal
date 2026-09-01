"""Context processor cung cấp site metadata và thông tin user/profile cho tất cả templates."""
from apps.announcements.models import Announcement
from django.utils import timezone


def site_context(request):
    ctx = {
        'site_name': 'Khai Technology',
        'domain': 'khai.local',
        'dc': 'DC-01',
        'unread_announcements': 0,
        'today_meetings_count': 0,
        'unread_payroll_count': 0,
    }
    if request.user.is_authenticated:
        try:
            ctx['user_profile'] = request.user.userprofile
            ctx['user_role'] = request.user.userprofile.role
        except Exception:
            ctx['user_profile'] = None
            ctx['user_role'] = 'employee'
        ctx['unread_announcements'] = Announcement.objects.filter(is_active=True).count()

        # Today's meetings count
        try:
            from apps.meetings.models import MeetingAttendee
            today = timezone.now().date()
            ctx['today_meetings_count'] = MeetingAttendee.objects.filter(
                user=request.user,
                meeting__start_time__date=today,
            ).count()
        except Exception:
            pass

        # Unread payroll count
        try:
            from apps.payroll.models import PayrollNotification
            ctx['unread_payroll_count'] = PayrollNotification.objects.filter(
                employee=request.user,
                status='sent',
                is_read=False,
            ).count()
        except Exception:
            pass
    return ctx
