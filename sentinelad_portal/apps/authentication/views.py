from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm
from apps.authentication.models import UserProfile


@csrf_exempt
@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Ensure UserProfile exists
                profile, _ = UserProfile.objects.get_or_create(user=user)
                if hasattr(user, '_ad_role'):
                    profile.role = user._ad_role
                    profile.department = getattr(user, '_ad_department', '')
                    profile.last_login_ip = request.META.get('REMOTE_ADDR')
                    profile.save()
                messages.success(request, f'Chào mừng, {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng. Vui lòng thử lại.')

    from django.conf import settings
    return render(request, 'auth/login.html', {
        'form': form,
        'page_title': 'Đăng nhập - SentinelAD Enterprise Portal',
        'ldap_mock_mode': getattr(settings, 'LDAP_MOCK_MODE', True),
    })


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất thành công.')
    return redirect('login')
