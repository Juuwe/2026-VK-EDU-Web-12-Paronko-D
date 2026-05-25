from django.urls import path
from django.contrib.auth.views import LogoutView
from core import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('logout/', LogoutView.as_view(), name='logout')
]
