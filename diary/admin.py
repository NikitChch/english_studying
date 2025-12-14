from django.contrib import admin
from .models import Grade, Attendance, Schedule

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'value', 'teacher', 'date', 'created_at')
    list_filter = ('subject', 'teacher', 'date', 'value')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'teacher__username')
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('student', 'teacher', 'subject', 'value', 'comment', 'date')
        }),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'teacher')
    list_filter = ('subject', 'teacher', 'date', 'status')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('student', 'teacher', 'subject', 'date', 'status')
        }),
    )

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('group', 'get_day_display', 'time_start', 'time_end', 'subject', 'teacher', 'classroom')
    list_filter = ('group', 'day', 'subject', 'teacher', 'is_active')
    search_fields = ('subject', 'teacher__username', 'classroom')
    
    fieldsets = (
        (None, {
            'fields': ('group', 'day', 'time_start', 'time_end', 'subject', 'teacher', 'classroom', 'is_active')
        }),
    )