import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, CourseModule
from django.utils import timezone
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Загружает тестовые курсы из JSON файла'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('data', 'test_courses.json')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден!'))
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                courses_data = json.load(file)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка чтения файла: {e}'))
            return
        
        teacher, created = User.objects.get_or_create(
            username='test_teacher',
            defaults={
                'email': 'teacher@example.com',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'user_type': 'teacher',
                'specialization': 'Общий английский, подготовка к экзаменам',
                'experience': 5,
                'is_staff': True,
                'is_active': True
            }
        )
        
        if created:
            teacher.set_password('testpassword123')
            teacher.save()
            self.stdout.write(self.style.SUCCESS('Создан тестовый преподаватель'))
        
        created_count = 0
        updated_count = 0
        
        for course_data in courses_data:
            try:
                start_date = datetime.strptime(course_data['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(course_data['end_date'], '%Y-%m-%d').date()
                
                course, created = Course.objects.update_or_create(
                    name=course_data['name'],
                    defaults={
                        'description': course_data['description'],
                        'level': course_data['level'],
                        'duration_weeks': course_data['duration_weeks'],
                        'price': course_data['price'],
                        'teacher': teacher,
                        'start_date': start_date,
                        'end_date': end_date,
                        'max_students': course_data['max_students'],
                        'current_students': 0
                    }
                )
                
                if created:
                    self.create_modules_for_course(course)
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Создан курс: {course.name}'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'Обновлен курс: {course.name}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при создании курса {course_data.get("name", "Unknown")}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'Загрузка завершена. Создано: {created_count}, Обновлено: {updated_count}'
        ))
    
    def create_modules_for_course(self, course):
        modules_data = [
            {
                'title': 'Введение и основы',
                'description': 'Знакомство с курсом, основные понятия, постановка целей',
                'order': 1,
                'duration_hours': 2
            },
            {
                'title': 'Основы грамматики',
                'description': 'Изучение базовых грамматических конструкций',
                'order': 2,
                'duration_hours': 4
            },
            {
                'title': 'Словарный запас',
                'description': 'Расширение словарного запаса по теме курса',
                'order': 3,
                'duration_hours': 3
            },
            {
                'title': 'Практика аудирования',
                'description': 'Тренировка восприятия английской речи на слух',
                'order': 4,
                'duration_hours': 3
            },
            {
                'title': 'Разговорная практика',
                'description': 'Отработка диалогов и монологов на английском',
                'order': 5,
                'duration_hours': 4
            },
            {
                'title': 'Чтение и понимание',
                'description': 'Работа с текстами, развитие навыков чтения',
                'order': 6,
                'duration_hours': 3
            },
            {
                'title': 'Письменная практика',
                'description': 'Написание текстов, эссе, писем на английском',
                'order': 7,
                'duration_hours': 4
            },
            {
                'title': 'Итоговый проект',
                'description': 'Выполнение итогового задания, закрепление материала',
                'order': 8,
                'duration_hours': 6
            }
        ]
        
        num_modules = min(course.duration_weeks // 2, 8)
        
        for i in range(num_modules):
            module_data = modules_data[i]
            CourseModule.objects.create(
                course=course,
                title=module_data['title'],
                description=module_data['description'],
                order=module_data['order'],
                duration_hours=module_data['duration_hours']
            )