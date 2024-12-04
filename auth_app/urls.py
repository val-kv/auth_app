from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('auth/link_telegram/', views.link_telegram, name='link_telegram'),
]
