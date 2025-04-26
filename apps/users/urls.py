from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, UserListView, RefreshTokenView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh-token/',RefreshTokenView.as_view(), name='refresh-token'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('users/all/', UserListView.as_view(), name='user-list')
]

