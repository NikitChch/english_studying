from django.contrib import admin
from .models import Course, CourseOrder, CourseModule

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'teacher', 'start_date', 'end_date', 
                    'price', 'current_students', 'max_students', 'is_available']
    list_filter = ['level', 'start_date', 'teacher']
    search_fields = ['name', 'description', 'teacher__username']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'level', 'duration_weeks')
        }),
        ('Финансы и расписание', {
            'fields': ('price', 'start_date', 'end_date')
        }),
        ('Персонал и студенты', {
            'fields': ('teacher', 'max_students', 'current_students')
        }),
    )


@admin.register(CourseOrder)
class CourseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'student', 'order_date', 'status', 
                    'progress', 'price_paid']
    list_filter = ['status', 'order_date', 'course__level']
    search_fields = ['student__username', 'course__name']
    list_editable = ['status', 'progress']


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration_hours']
    list_filter = ['course']
    search_fields = ['title', 'course__name']