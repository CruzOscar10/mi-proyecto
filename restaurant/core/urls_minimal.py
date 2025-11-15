# core/urls_minimal.py (temporal)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.custom_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]