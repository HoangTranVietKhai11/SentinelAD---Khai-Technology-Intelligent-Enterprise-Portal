from django.urls import path
from . import views
urlpatterns = [
    path('', views.audit_list, name='audit_list'),
    path('ai-analysis/', views.ai_analysis, name='ai_analysis'),
]
