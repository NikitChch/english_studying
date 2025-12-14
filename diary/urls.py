from django.urls import path
from . import views

app_name = 'diary'

urlpatterns = [
    path('', views.diary, name='diary'),
    path('api/add_grade/', views.add_grade_api, name='add_grade_api'),
    path('api/mark_attendance/', views.mark_attendance_api, name='mark_attendance_api'),
    path('api/student/<int:student_id>/', views.get_student_details_api, name='student_details_api'),
]