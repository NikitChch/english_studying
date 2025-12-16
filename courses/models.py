from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Course(models.Model):
    
    LEVEL_CHOICES = [
        ('A1', 'A1 - Начальный'),
        ('A2', 'A2 - Элементарный'),
        ('B1', 'B1 - Средний'),
        ('B2', 'B2 - Выше среднего'),
        ('C1', 'C1 - Продвинутый'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание курса")
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name="Уровень")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    
    teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'user_type': 'teacher'},
        verbose_name="Преподаватель",
        related_name='taught_courses'
    )
    
    start_date = models.DateField(verbose_name="Дата начала курса")
    end_date = models.DateField(verbose_name="Дата окончания курса")
    max_students = models.IntegerField(verbose_name="Максимальное количество студентов", default=20)
    current_students = models.IntegerField(default=0, verbose_name="Текущее количество студентов")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    @property
    def total_income(self):
        try:
            return self.current_students * float(self.price)
        except (ValueError, TypeError):
            return 0
    
    @property
    def duration_weeks(self):
        if self.start_date and self.end_date:
            duration_days = (self.end_date - self.start_date).days
            return duration_days // 7
        return 0
    
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def duration_months(self):
        if self.start_date and self.end_date:
            months = (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
            return months
        return 0
    
    def is_available(self):
        return self.current_students < self.max_students
    
    def available_seats(self):
        return self.max_students - self.current_students
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
    
    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['start_date']


class CourseModule(models.Model):
    
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='modules',
        verbose_name="Курс"
    )
    
    title = models.CharField(max_length=200, verbose_name="Название модуля")
    description = models.TextField(verbose_name="Описание модуля")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    duration_hours = models.IntegerField(default=2, verbose_name="Длительность (часов)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"
    
    class Meta:
        verbose_name = "Модуль курса"
        verbose_name_plural = "Модули курса"
        ordering = ['order']


class CourseOrder(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('in_progress', 'В процессе обучения'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        verbose_name="Курс",
        related_name='orders'
    )
    
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Студент",
        related_name='course_orders'
    )
    
    completed_modules = models.ManyToManyField(
        CourseModule,
        blank=True,
        verbose_name="Пройденные модули",
        related_name='completed_orders'
    )
    cancellation_reason = models.TextField(
        blank=True, 
        verbose_name="Причина отмены"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Комментарии студента при записи"
    )
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    start_date = models.DateField(verbose_name="Дата начала обучения")
    expected_end_date = models.DateField(verbose_name="Планируемая дата окончания")
    actual_end_date = models.DateField(null=True, blank=True, verbose_name="Фактическая дата окончания")
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name="Статус заказа"
    )
    
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Оплаченная сумма")
    
    progress = models.IntegerField(default=0, verbose_name="Прогресс (%)")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Последняя активность")
    
    rating = models.IntegerField(
        null=True, 
        blank=True, 
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Оценка курса"
    )
    
    feedback = models.TextField(blank=True, verbose_name="Отзыв о курсе")
    
    def calculate_progress(self):
        total_modules = self.course.modules.count()
        if total_modules == 0:
            return 0
            
        completed_count = self.completed_modules.count()
        progress = (completed_count / total_modules) * 100
        return round(progress, 1)
    
    def cancel_order(self, reason=None):
        if self.status in ['pending', 'paid', 'in_progress']:
            self.status = 'cancelled'
            
            if reason:
                self.cancellation_reason = reason
            
            self.course.current_students -= 1
            if self.course.current_students < 0:
                self.course.current_students = 0
            self.course.save()
            
            self.save()
            return True
        return False
    
    def complete_course_order(self):
        self.status = 'completed'
        self.actual_end_date = timezone.now().date()
        self.progress = 100
        
        self.course.current_students -= 1
        if self.course.current_students < 0:
            self.course.current_students = 0
        self.course.save()
        
        self.save()
        return True
    
    def can_be_cancelled(self):
        return self.status in ['pending', 'paid', 'in_progress']
    
    def can_be_deleted(self):
        return self.status in ['completed', 'cancelled']
    
    @property
    def completed_modules_count(self):
        return self.completed_modules.count()
    
    @property
    def total_modules_count(self):
        return self.course.modules.count()
    
    def complete_course(self):
        all_modules = self.course.modules.all()
        for module in all_modules:
            if not self.completed_modules.filter(id=module.id).exists():
                self.completed_modules.add(module)
        
        self.progress = 100
        self.actual_end_date = timezone.now().date()
        self.status = 'completed'
        
        self.course.current_students -= 1
        if self.course.current_students < 0:
            self.course.current_students = 0
        self.course.save()
        
        self.save()
    
    def days_remaining(self):
        if self.status == 'completed':
            return 0
        remaining = (self.expected_end_date - timezone.now().date()).days
        return max(0, remaining)
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.course.name} - {self.student.username}"
    
    class Meta:
        verbose_name = "Заказ курса"
        verbose_name_plural = "Заказы курсов"
        ordering = ['-order_date']
        unique_together = ['course', 'student']