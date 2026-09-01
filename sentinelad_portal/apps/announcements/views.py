from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Announcement
from apps.audit.middleware import log_action


@login_required
def announcement_list(request):
    category = request.GET.get('category', '')
    announcements = Announcement.objects.filter(is_active=True)
    if category:
        announcements = announcements.filter(category=category)

    return render(request, 'announcements/announcement_list.html', {
        'page_title': 'Bảng tin Thông báo - Khai Technology',
        'announcements': announcements,
        'selected_category': category,
        'category_choices': Announcement.CATEGORY_CHOICES,
    })


@login_required
def announcement_create(request):
    if request.method == 'POST':
        ann = Announcement(
            title=request.POST.get('title', '').strip(),
            content=request.POST.get('content', '').strip(),
            level=request.POST.get('level', 'normal'),
            category=request.POST.get('category', 'general'),
            pinned=request.POST.get('pinned') == 'on',
            created_by=request.user,
        )
        ann.save()
        log_action(request.user, 'CREATE', 'Announcement', ann.pk, ann.title,
                   f'Created announcement: {ann.title}', request.META.get('REMOTE_ADDR'))
        messages.success(request, 'Đã đăng thông báo thành công.')
        return redirect('announcement_list')
    return render(request, 'announcements/announcement_form.html', {
        'page_title': 'Đăng Thông báo',
        'level_choices': Announcement.LEVEL_CHOICES,
        'category_choices': Announcement.CATEGORY_CHOICES,
    })


@login_required
def announcement_edit(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.title = request.POST.get('title', ann.title).strip()
        ann.content = request.POST.get('content', ann.content).strip()
        ann.level = request.POST.get('level', ann.level)
        ann.category = request.POST.get('category', ann.category)
        ann.pinned = request.POST.get('pinned') == 'on'
        ann.save()
        log_action(request.user, 'UPDATE', 'Announcement', ann.pk, ann.title,
                   f'Updated announcement: {ann.title}', request.META.get('REMOTE_ADDR'))
        messages.success(request, 'Đã cập nhật thông báo.')
        return redirect('announcement_list')
    return render(request, 'announcements/announcement_form.html', {
        'page_title': 'Sửa Thông báo',
        'ann': ann,
        'level_choices': Announcement.LEVEL_CHOICES,
        'category_choices': Announcement.CATEGORY_CHOICES,
    })


@login_required
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        title = ann.title
        ann.delete()
        log_action(request.user, 'DELETE', 'Announcement', pk, title,
                   f'Deleted announcement: {title}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Đã xóa thông báo "{title}".')
        return redirect('announcement_list')
    return render(request, 'announcements/announcement_confirm_delete.html', {'ann': ann})
