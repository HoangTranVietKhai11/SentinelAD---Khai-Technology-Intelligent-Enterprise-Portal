from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Ticket, TicketComment
from apps.audit.middleware import log_action


@login_required
def ticket_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    tickets = Ticket.objects.select_related('created_by', 'assigned_to').all()
    # Employees see only their own tickets
    try:
        role = request.user.userprofile.role
    except Exception:
        role = 'employee'
    if role == 'employee':
        tickets = tickets.filter(created_by=request.user)
    if query:
        tickets = tickets.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    return render(request, 'tickets/ticket_list.html', {
        'page_title': 'Ticket Hỗ trợ Kỹ thuật',
        'tickets': tickets,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'query': query, 'status_filter': status_filter, 'priority_filter': priority_filter,
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comments = ticket.comments.select_related('author').all()
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            TicketComment.objects.create(ticket=ticket, author=request.user, content=content)
            messages.success(request, 'Đã thêm phản hồi.')
            return redirect('ticket_detail', pk=pk)
    return render(request, 'tickets/ticket_detail.html', {
        'page_title': f'Ticket #{ticket.pk}',
        'ticket': ticket, 'comments': comments,
        'status_choices': Ticket.STATUS_CHOICES,
    })


@login_required
def ticket_create(request):
    if request.method == 'POST':
        ticket = Ticket(
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            priority=request.POST.get('priority', 'medium'),
            created_by=request.user,
        )
        ticket.save()
        log_action(request.user, 'CREATE', 'Ticket', ticket.pk, ticket.title,
                   f'Created ticket: {ticket.title}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Ticket #{ticket.pk} đã được tạo thành công.')
        return redirect('ticket_detail', pk=ticket.pk)
    return render(request, 'tickets/ticket_form.html', {
        'page_title': 'Tạo Ticket mới',
        'priority_choices': Ticket.PRIORITY_CHOICES,
    })


@login_required
def ticket_update_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')
        resolution = request.POST.get('resolution', '')
        if new_status in dict(Ticket.STATUS_CHOICES):
            old_status = ticket.status
            ticket.status = new_status
            if new_status in ('resolved', 'closed'):
                ticket.resolved_at = timezone.now()
                ticket.resolution = resolution
            if assigned_to_id:
                from django.contrib.auth.models import User
                try:
                    ticket.assigned_to = User.objects.get(pk=assigned_to_id)
                except User.DoesNotExist:
                    pass
            ticket.save()
            log_action(request.user, 'UPDATE', 'Ticket', ticket.pk, ticket.title,
                       f'Status changed: {old_status} → {new_status}', request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Ticket #{ticket.pk} đã cập nhật trạng thái: {ticket.get_status_display()}')
    return redirect('ticket_detail', pk=pk)


@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        title = ticket.title
        ticket.delete()
        log_action(request.user, 'DELETE', 'Ticket', pk, title,
                   f'Deleted ticket: {title}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Đã xóa ticket "{title}".')
        return redirect('ticket_list')
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})
