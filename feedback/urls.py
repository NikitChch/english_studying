from django.urls import path
from .views import FeedbackView, FeedbackSuccessView

app_name = 'feedback'

urlpatterns = [
    path('', FeedbackView.as_view(), name='feedback'),
    path('success/', FeedbackSuccessView.as_view(), name='success'),
]