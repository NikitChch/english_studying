from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    
    path('password_change/', 
         views.CustomPasswordChangeView.as_view(), 
         name='password_change'),
    path('password_change/done/', 
         views.CustomPasswordChangeDoneView.as_view(), 
         name='password_change_done'),
    
    path('password_reset/', 
         views.CustomPasswordResetView.as_view(), 
         name='password_reset'),
    path('password_reset/code/', 
         views.PasswordResetCodeView.as_view(), 
         name='password_reset_code'),
    path('password_reset/resend/', 
         views.ResendResetCodeView.as_view(), 
         name='resend_reset_code'),
    path('password_reset/confirm/', 
         views.CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('reset/done/', 
         views.CustomPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
    
    path('send-test-email-api/', views.send_test_email_api, name='send_test_email_api'),
]