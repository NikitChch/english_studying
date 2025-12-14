from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    
    USER_TYPE_CHOICES = (
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        verbose_name='Тип пользователя'
    )
    
    group = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Для студентов: A1, A2, B1, B2, C1'
    )
    
    level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Уровень английского'
    )
    
    specialization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Специализация'
    )
    
    experience = models.IntegerField(
        default=0,
        verbose_name='Опыт работы (лет)',
        blank=True,
        null=False
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name='Фотография профиля'
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'


class PasswordResetCode(models.Model):
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reset_codes',
        verbose_name='Пользователь'
    )
    
    code = models.CharField(
        max_length=6,
        verbose_name='Код восстановления'
    )
    
    email = models.EmailField(verbose_name='Email для восстановления')
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='Срок действия'
    )
    
    is_used = models.BooleanField(
        default=False,
        verbose_name='Использован'
    )
    
    class Meta:
        verbose_name = 'Код восстановления пароля'
        verbose_name_plural = 'Коды восстановления пароля'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Код {self.code} для {self.email}'
    
    def is_valid(self):
        return (
            not self.is_used and 
            timezone.now() <= self.expires_at
        )
    
    def mark_as_used(self):
        self.is_used = True
        self.save()
    
    @classmethod
    def generate_code(cls, user, email):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        code = ''.join(random.choices(string.digits, k=6))
        
        reset_code = cls.objects.create(
            user=user,
            code=code,
            email=email,
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        
        return reset_code
    
    @classmethod
    def validate_code(cls, email, code):
        try:
            reset_code = cls.objects.get(
                email=email,
                code=code,
                is_used=False
            )
            
            if reset_code.is_valid():
                return reset_code
            else:
                return None
        except cls.DoesNotExist:
            return None