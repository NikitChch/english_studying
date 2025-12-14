from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser
from diary.models import Schedule

class Command(BaseCommand):
    help = 'Создает расписание по умолчанию для всех групп'

    def handle(self, *args, **options):
        teachers = CustomUser.objects.filter(user_type='teacher')
        
        if not teachers.exists():
            self.stdout.write(self.style.WARNING('Нет преподавателей в системе! Сначала создайте преподавателей.'))
            return
        
        teacher_rustam, _ = CustomUser.objects.get_or_create(
            username='rustam_teacher',
            defaults={
                'email': 'rustam@example.com',
                'first_name': 'Рустам',
                'last_name': 'Емельянов',
                'user_type': 'teacher',
                'specialization': 'Грамматика и аудирование',
                'experience': 5,
                'is_staff': True,
                'is_active': True
            }
        )
        teacher_rustam.set_password('password123')
        teacher_rustam.save()
        
        teacher_andrey, _ = CustomUser.objects.get_or_create(
            username='andrey_teacher',
            defaults={
                'email': 'andrey@example.com',
                'first_name': 'Андрей',
                'last_name': 'Синиелюбов',
                'user_type': 'teacher',
                'specialization': 'Бизнес-английский и письмо',
                'experience': 7,
                'is_staff': True,
                'is_active': True
            }
        )
        teacher_andrey.set_password('password123')
        teacher_andrey.save()
        
        teacher_nikita, _ = CustomUser.objects.get_or_create(
            username='qw',
            defaults={
                'email': 'qw@gmail.com',
                'first_name': 'Никита',
                'last_name': 'Чеченев',
                'user_type': 'teacher',
                'specialization': 'Разговорная практика и словарь',
                'experience': 4,
                'is_staff': True,
                'is_active': True
            }
        )
        teacher_nikita.set_password('Nikita228')
        teacher_nikita.save()
        
        default_schedule = [
            {'group': 'A1', 'day': 'monday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Грамматика', 'classroom': '101', 'teacher': teacher_rustam},
            {'group': 'A1', 'day': 'monday', 'time_start': '11:00', 'time_end': '12:30', 'subject': 'Разговорная практика', 'classroom': '102', 'teacher': teacher_andrey},
            {'group': 'A1', 'day': 'tuesday', 'time_start': '10:00', 'time_end': '11:30', 'subject': 'Словарь', 'classroom': '103', 'teacher': teacher_nikita},
            {'group': 'A1', 'day': 'wednesday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Аудирование', 'classroom': '101', 'teacher': teacher_rustam},
            {'group': 'A1', 'day': 'thursday', 'time_start': '16:00', 'time_end': '17:30', 'subject': 'Письмо', 'classroom': '104', 'teacher': teacher_andrey},
            {'group': 'A1', 'day': 'friday', 'time_start': '13:00', 'time_end': '14:30', 'subject': 'Чтение', 'classroom': '105', 'teacher': teacher_nikita},
            
            {'group': 'A2', 'day': 'monday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Бизнес-английский', 'classroom': '201', 'teacher': teacher_andrey},
            {'group': 'A2', 'day': 'tuesday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Грамматика', 'classroom': '202', 'teacher': teacher_rustam},
            {'group': 'A2', 'day': 'wednesday', 'time_start': '11:00', 'time_end': '12:30', 'subject': 'Разговорная практика', 'classroom': '203', 'teacher': teacher_nikita},
            {'group': 'A2', 'day': 'thursday', 'time_start': '13:00', 'time_end': '14:30', 'subject': 'Письмо', 'classroom': '201', 'teacher': teacher_andrey},
            {'group': 'A2', 'day': 'friday', 'time_start': '15:00', 'time_end': '16:30', 'subject': 'Аудирование', 'classroom': '204', 'teacher': teacher_nikita},
            
            {'group': 'B1', 'day': 'monday', 'time_start': '16:00', 'time_end': '17:30', 'subject': 'Подготовка к IELTS', 'classroom': '301', 'teacher': teacher_nikita},
            {'group': 'B1', 'day': 'tuesday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Бизнес-английский', 'classroom': '302', 'teacher': teacher_andrey},
            {'group': 'B1', 'day': 'wednesday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Грамматика', 'classroom': '303', 'teacher': teacher_rustam},
            {'group': 'B1', 'day': 'thursday', 'time_start': '11:00', 'time_end': '12:30', 'subject': 'Разговорный клуб', 'classroom': '301', 'teacher': teacher_nikita},
            {'group': 'B1', 'day': 'friday', 'time_start': '13:00', 'time_end': '14:30', 'subject': 'Письмо', 'classroom': '304', 'teacher': teacher_andrey},
            
            {'group': 'B2', 'day': 'monday', 'time_start': '10:00', 'time_end': '11:30', 'subject': 'Академическое письмо', 'classroom': '401', 'teacher': teacher_rustam},
            {'group': 'B2', 'day': 'tuesday', 'time_start': '16:00', 'time_end': '17:30', 'subject': 'Деловая переписка', 'classroom': '402', 'teacher': teacher_andrey},
            {'group': 'B2', 'day': 'wednesday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Публичные выступления', 'classroom': '403', 'teacher': teacher_nikita},
            {'group': 'B2', 'day': 'thursday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Аналитическое чтение', 'classroom': '401', 'teacher': teacher_rustam},
            
            {'group': 'C1', 'day': 'monday', 'time_start': '18:00', 'time_end': '19:30', 'subject': 'Профессиональный английский', 'classroom': '501', 'teacher': teacher_nikita},
            {'group': 'C1', 'day': 'tuesday', 'time_start': '18:00', 'time_end': '19:30', 'subject': 'Научная литература', 'classroom': '502', 'teacher': teacher_andrey},
            {'group': 'C1', 'day': 'thursday', 'time_start': '18:00', 'time_end': '19:30', 'subject': 'Переводческое дело', 'classroom': '501', 'teacher': teacher_rustam},
        ]
        
        created_count = 0
        updated_count = 0
        
        for lesson_data in default_schedule:
            try:
                existing = Schedule.objects.filter(
                    group=lesson_data['group'],
                    day=lesson_data['day'],
                    time_start=lesson_data['time_start'],
                    time_end=lesson_data['time_end']
                ).first()
                
                if not existing:
                    schedule = Schedule.objects.create(
                        group=lesson_data['group'],
                        day=lesson_data['day'],
                        time_start=lesson_data['time_start'],
                        time_end=lesson_data['time_end'],
                        subject=lesson_data['subject'],
                        teacher=lesson_data['teacher'],
                        classroom=lesson_data['classroom'],
                        is_active=True
                    )
                    created_count += 1
                    self.stdout.write(f"Создано: {schedule}")
                else:
                    existing.teacher = lesson_data['teacher']
                    existing.subject = lesson_data['subject']
                    existing.classroom = lesson_data['classroom']
                    existing.is_active = True
                    existing.save()
                    updated_count += 1
                    self.stdout.write(f"Обновлено: {existing}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при создании/обновлении расписания: {e}'))
                self.stdout.write(f'Данные: {lesson_data}')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Готово!'))
        self.stdout.write(f'Создано новых: {created_count}')
        self.stdout.write(f'Обновлено: {updated_count}')
        self.stdout.write(f'Всего расписаний в базе: {Schedule.objects.count()}')
        
        self.stdout.write("\nСтатистика по группам:")
        for group in ['A1', 'A2', 'B1', 'B2', 'C1']:
            count = Schedule.objects.filter(group=group).count()
            teachers_list = Schedule.objects.filter(group=group).values_list('teacher__username', flat=True).distinct()
            self.stdout.write(f"  Группа {group}: {count} занятий (Преподаватели: {', '.join(set(teachers_list))})")
        
        self.stdout.write("\nСтатистика по преподавателям:")
        for teacher in [teacher_rustam, teacher_andrey, teacher_nikita]:
            count = Schedule.objects.filter(teacher=teacher).count()
            groups = Schedule.objects.filter(teacher=teacher).values_list('group', flat=True).distinct()
            self.stdout.write(f"  {teacher.get_full_name()}: {count} занятий (Группы: {', '.join(set(groups))})")