from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login')),
    path('auth/', include('apps.authentication.urls')),
    path('dashboard/', include('apps.core.urls')),
    path('employees/', include('apps.employees.urls')),
    path('assets/', include('apps.assets.urls')),
    path('tickets/', include('apps.tickets.urls')),
    path('announcements/', include('apps.announcements.urls')),
    path('audit/', include('apps.audit.urls')),
    path('meetings/', include('apps.meetings.urls')),
    path('payroll/', include('apps.payroll.urls')),
]

