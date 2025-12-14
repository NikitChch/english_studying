from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='home'),
    path('api/feedbacks/', views.api_feedbacks, name='api_feedbacks'),
]