from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Meeting, MeetingAttendee


@login_required
def meeting_list(request):
    now = timezone.now()
    view_filter = request.GET.get('filter', 'upcoming')

    if view_filter == 'today':
        meetings = Meeting.objects.filter(
            start_time__date=now.date()
        )
    elif view_filter == 'week':
        week_end = now + timedelta(days=7)
        meetings = Meeting.objects.filter(
            start_time__gte=now,
            start_time__lte=week_end
        )
    elif view_filter == 'past':
        meetings = Meeting.objects.filter(start_time__lt=now).order_by('-start_time')
    else:  # upcoming
        meetings = Meeting.objects.filter(start_time__gte=now)

    context = {
        'page_title': 'Lịch họp - Khai Technology',
        'meetings': meetings,
        'current_filter': view_filter,
        'now': now,
    }
    return render(request, 'meetings/meeting_list.html', context)


@login_required
def meeting_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        meeting_type = request.POST.get('meeting_type', 'team')
        location = request.POST.get('location', '').strip()
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        priority = request.POST.get('priority', 'normal')
        is_recurring = request.POST.get('is_recurring') == 'on'
        attendee_ids = request.POST.getlist('attendees')

        if not title or not start_time or not end_time:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc.')
            return redirect('meeting_create')

        meeting = Meeting.objects.create(
            title=title,
            description=description,
            meeting_type=meeting_type,
            location=location,
            start_time=start_time,
            end_time=end_time,
            organizer=request.user,
            priority=priority,
            is_recurring=is_recurring,
        )

        # Add attendees
        for uid in attendee_ids:
            try:
                user = User.objects.get(pk=uid)
                MeetingAttendee.objects.create(meeting=meeting, user=user)
            except User.DoesNotExist:
                pass

        messages.success(request, f'Đã tạo cuộc họp "{title}" thành công!')
        return redirect('meeting_list')

    users = User.objects.filter(is_active=True).order_by('first_name')
    context = {
        'page_title': 'Tạo cuộc họp mới',
        'users': users,
        'meeting_types': Meeting.TYPE_CHOICES,
        'priority_choices': Meeting.PRIORITY_CHOICES,
    }
    return render(request, 'meetings/meeting_form.html', context)


@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    attendees = meeting.attendees.select_related('user').all()

    # Handle RSVP
    if request.method == 'POST':
        rsvp_status = request.POST.get('rsvp')
        if rsvp_status in ('accepted', 'declined'):
            attendee, created = MeetingAttendee.objects.get_or_create(
                meeting=meeting, user=request.user,
                defaults={'status': rsvp_status}
            )
            if not created:
                attendee.status = rsvp_status
                attendee.save()
            messages.success(request, 'Đã cập nhật trạng thái tham dự.')
            return redirect('meeting_detail', pk=pk)

    # Check current user's RSVP status
    user_rsvp = None
    try:
        user_attendee = MeetingAttendee.objects.get(meeting=meeting, user=request.user)
        user_rsvp = user_attendee.status
    except MeetingAttendee.DoesNotExist:
        pass

    context = {
        'page_title': meeting.title,
        'meeting': meeting,
        'attendees': attendees,
        'user_rsvp': user_rsvp,
    }
    return render(request, 'meetings/meeting_detail.html', context)


@login_required
def meeting_update(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        meeting.title = request.POST.get('title', meeting.title).strip()
        meeting.description = request.POST.get('description', '').strip()
        meeting.meeting_type = request.POST.get('meeting_type', meeting.meeting_type)
        meeting.location = request.POST.get('location', '').strip()
        meeting.start_time = request.POST.get('start_time', meeting.start_time)
        meeting.end_time = request.POST.get('end_time', meeting.end_time)
        meeting.priority = request.POST.get('priority', meeting.priority)
        meeting.is_recurring = request.POST.get('is_recurring') == 'on'
        meeting.save()

        # Update attendees
        attendee_ids = request.POST.getlist('attendees')
        meeting.attendees.exclude(user_id__in=attendee_ids).delete()
        for uid in attendee_ids:
            try:
                user = User.objects.get(pk=uid)
                MeetingAttendee.objects.get_or_create(meeting=meeting, user=user)
            except User.DoesNotExist:
                pass

        messages.success(request, f'Đã cập nhật cuộc họp "{meeting.title}".')
        return redirect('meeting_detail', pk=pk)

    users = User.objects.filter(is_active=True).order_by('first_name')
    current_attendee_ids = list(meeting.attendees.values_list('user_id', flat=True))
    context = {
        'page_title': f'Sửa: {meeting.title}',
        'meeting': meeting,
        'users': users,
        'meeting_types': Meeting.TYPE_CHOICES,
        'priority_choices': Meeting.PRIORITY_CHOICES,
        'current_attendee_ids': current_attendee_ids,
        'is_edit': True,
    }
    return render(request, 'meetings/meeting_form.html', context)


@login_required
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        title = meeting.title
        meeting.delete()
        messages.success(request, f'Đã xoá cuộc họp "{title}".')
    return redirect('meeting_list')
