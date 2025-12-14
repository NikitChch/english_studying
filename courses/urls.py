from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    
    path('my-courses/', views.my_courses, name='my_courses'),
    path('<int:pk>/enroll/', views.course_enroll, name='course_enroll'),
    path('order/<int:order_id>/', views.course_student_detail, name='course_student_detail'),
    path('order/<int:order_id>/complete/', views.complete_course, name='complete_course'),
    path('order/<int:order_id>/cancel/', views.cancel_course, name='cancel_course'),
    path('order/<int:order_id>/delete/', views.delete_course, name='delete_course'),
    path('order/<int:order_id>/update-progress/', views.update_progress, name='update_progress'),
    path('order/<int:order_id>/module/<int:module_id>/complete/', 
         views.mark_module_complete, name='mark_module_complete'),
    
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/courses/create/', views.create_course, name='create_course'),
    path('teacher/courses/<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('teacher/courses/<int:pk>/delete/', views.delete_course_teacher, name='delete_course_teacher'),
    path('teacher/courses/<int:pk>/modules/', views.add_modules, name='add_modules'),
    path('teacher/courses/<int:pk>/students/', views.course_students, name='course_students'),
    path('teacher/courses/<int:pk>/detail/', views.teacher_course_detail, name='teacher_course_detail'),
    
]