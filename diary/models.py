from django.db import models
from users.models import CustomUser
from django.utils import timezone


class Grade(models.Model):
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='grades',
        limit_choices_to={'user_type': 'student'},
        verbose_name='Студент'
    )
    
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='given_grades',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='Преподаватель'
    )
    
    subject = models.CharField(
        max_length=100,
        verbose_name='Предмет'
    )
    
    value = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='Оценка'
    )
    
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )
    
    date = models.DateField(
        default=timezone.now,
        verbose_name='Дата выставления'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f'{self.student} - {self.subject}: {self.value}'


class Attendance(models.Model):
    
    STATUS_CHOICES = (
        ('present', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('late', 'Опоздал'),
    )
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'user_type': 'student'},
        verbose_name='Студент'
    )
    
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='marked_attendance',
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='Преподаватель'
    )
    
    subject = models.CharField(
        max_length=100,
        verbose_name='Предмет'
    )
    
    date = models.DateField(
        verbose_name='Дата занятия'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        ordering = ['-date', '-created_at']
        unique_together = ['student', 'subject', 'date']
    
    def __str__(self):
        return f'{self.student} - {self.subject} ({self.date}): {self.get_status_display()}'


class Schedule(models.Model):
    
    DAY_CHOICES = (
        ('monday', 'Понедельник'),
        ('tuesday', 'Вторник'),
        ('wednesday', 'Среда'),
        ('thursday', 'Четверг'),
        ('friday', 'Пятница'),
        ('saturday', 'Суббота'),
        ('sunday', 'Воскресенье'),
    )
    
    group = models.CharField(
        max_length=10,
        verbose_name='Группа'
    )
    
    day = models.CharField(
        max_length=10,
        choices=DAY_CHOICES,
        verbose_name='День недели'
    )
    
    time_start = models.TimeField(verbose_name='Время начала')
    time_end = models.TimeField(verbose_name='Время окончания')
    
    subject = models.CharField(
        max_length=100,
        verbose_name='Предмет'
    )
    
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'user_type': 'teacher'},
        verbose_name='Преподаватель'
    )
    
    classroom = models.CharField(
        max_length=20,
        verbose_name='Аудитория'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    
    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['group', 'day', 'time_start']
    
    def __str__(self):
        return f'{self.group} - {self.get_day_display()} {self.time_start}-{self.time_end}: {self.subject}'
    
    @property
    def time_range(self):
        return f'{self.time_start.strftime("%H:%M")} - {self.time_end.strftime("%H:%M")}'