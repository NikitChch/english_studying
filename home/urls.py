from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='home'),
    path('api/feedbacks/', views.api_feedbacks, name='api_feedbacks'),
    path('api/feedbacks/<int:feedback_id>/like/', views.api_toggle_like, name='api_toggle_like'),
]