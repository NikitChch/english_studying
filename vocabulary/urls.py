from django.urls import path
from . import views

app_name = 'vocabulary'

urlpatterns = [
    path('', views.vocabulary, name='vocabulary'),
]