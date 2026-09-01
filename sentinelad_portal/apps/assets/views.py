from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Asset
from apps.audit.middleware import log_action


@login_required
def asset_list(request):
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    assets = Asset.objects.all()
    if query:
        assets = assets.filter(
            Q(asset_tag__icontains=query) | Q(asset_name__icontains=query) |
            Q(serial_number__icontains=query) | Q(assigned_user_name__icontains=query)
        )
    if type_filter:
        assets = assets.filter(asset_type=type_filter)
    if status_filter:
        assets = assets.filter(status=status_filter)
    return render(request, 'assets/asset_list.html', {
        'page_title': 'Quản lý Tài sản CNTT',
        'assets': assets,
        'type_choices': Asset.TYPE_CHOICES,
        'status_choices': Asset.STATUS_CHOICES,
        'query': query, 'type_filter': type_filter, 'status_filter': status_filter,
    })


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, 'assets/asset_detail.html', {'page_title': asset.asset_name, 'asset': asset})


@login_required
def asset_create(request):
    if request.method == 'POST':
        asset = Asset(
            asset_tag=request.POST.get('asset_tag', ''),
            asset_name=request.POST.get('asset_name', ''),
            asset_type=request.POST.get('asset_type', 'other'),
            serial_number=request.POST.get('serial_number', ''),
            assigned_user_name=request.POST.get('assigned_user_name', ''),
            status=request.POST.get('status', 'in_stock'),
            notes=request.POST.get('notes', ''),
        )
        purchase_date = request.POST.get('purchase_date')
        warranty_date = request.POST.get('warranty_date')
        if purchase_date: asset.purchase_date = purchase_date
        if warranty_date: asset.warranty_date = warranty_date
        try:
            asset.save()
            log_action(request.user, 'CREATE', 'Asset', asset.pk, asset.asset_name,
                       f'Created asset: {asset.asset_tag}', request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Đã thêm tài sản "{asset.asset_name}".')
            return redirect('asset_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
    return render(request, 'assets/asset_form.html', {
        'page_title': 'Thêm Tài sản',
        'type_choices': Asset.TYPE_CHOICES,
        'status_choices': Asset.STATUS_CHOICES,
    })


@login_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.asset_name = request.POST.get('asset_name', asset.asset_name)
        asset.asset_type = request.POST.get('asset_type', asset.asset_type)
        asset.serial_number = request.POST.get('serial_number', '')
        asset.assigned_user_name = request.POST.get('assigned_user_name', '')
        asset.status = request.POST.get('status', asset.status)
        asset.notes = request.POST.get('notes', '')
        pd = request.POST.get('purchase_date')
        wd = request.POST.get('warranty_date')
        asset.purchase_date = pd if pd else None
        asset.warranty_date = wd if wd else None
        asset.save()
        log_action(request.user, 'UPDATE', 'Asset', asset.pk, asset.asset_name,
                   f'Updated asset: {asset.asset_tag}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Đã cập nhật tài sản "{asset.asset_name}".')
        return redirect('asset_list')
    return render(request, 'assets/asset_form.html', {
        'page_title': 'Sửa Tài sản', 'asset': asset,
        'type_choices': Asset.TYPE_CHOICES, 'status_choices': Asset.STATUS_CHOICES,
    })


@login_required
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        name = asset.asset_name
        asset.delete()
        log_action(request.user, 'DELETE', 'Asset', pk, name,
                   f'Deleted asset: {name}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Đã xóa tài sản "{name}".')
        return redirect('asset_list')
    return render(request, 'assets/asset_confirm_delete.html', {'asset': asset})
