from django.urls import path
from . import views

app_name = 'grammar'

urlpatterns = [
    path('', views.grammar, name='grammar'),
]