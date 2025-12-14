from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from users.models import CustomUser
from .models import Grade, Attendance, Schedule
from django.utils import timezone
from datetime import date, datetime

@login_required
def diary(request):
    user = request.user
    context = {
        'page_title': 'Дневник',
        'user': user,
    }
    
    if user.user_type == 'teacher':
        students = CustomUser.objects.filter(user_type='student')
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'name': student.get_full_name() or student.username,
                'email': student.email,
                'group': student.group,
                'level': student.level,
            })
        context['all_students_json'] = json.dumps(students_data)
        
        subjects_from_db = Grade.objects.values_list('subject', flat=True).distinct()
        if subjects_from_db.exists():
            subjects_list = list(subjects_from_db)
        else:
            subjects_list = [
                'Грамматика', 'Словарь', 'Аудирование', 'Письмо', 'Чтение', 'Разговорная практика',
                'Бизнес-английский', 'Подготовка к IELTS', 'Разговорный клуб', 'Академическое письмо',
                'Деловая переписка', 'Публичные выступления', 'Аналитическое чтение',
                'Профессиональный английский', 'Научная литература', 'Переводческое дело'
            ]
        
        context['subjects'] = subjects_list
    
    elif user.user_type == 'student':
        grades = Grade.objects.filter(student=user).select_related('teacher')
        attendance = Attendance.objects.filter(student=user).select_related('teacher')
        
        grades_data = []
        for grade in grades:
            grades_data.append({
                'id': grade.id,
                'subject': grade.subject,
                'value': str(grade.value),
                'comment': grade.comment or '',
                'date': grade.date.strftime('%Y-%m-%d'),
                'teacher_id': grade.teacher.id,
                'teacher_name': grade.teacher.get_full_name() or grade.teacher.username,
                'created_at': grade.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        attendance_data = []
        for record in attendance:
            attendance_data.append({
                'id': record.id,
                'date': record.date.strftime('%Y-%m-%d'),
                'subject': record.subject,
                'status': record.status,
                'teacher_id': record.teacher.id,
                'teacher_name': record.teacher.get_full_name() or record.teacher.username,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        context['student_grades_json'] = json.dumps(grades_data)
        context['student_attendance_json'] = json.dumps(attendance_data)
    
    return render(request, 'diary.html', context)

@csrf_exempt
@require_POST
@login_required
def add_grade_api(request):
    if request.user.user_type != 'teacher':
        return JsonResponse({'success': False, 'message': 'Доступ запрещен'}, status=403)
    
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        subject = data.get('subject')
        value = data.get('value')
        comment = data.get('comment', '')
        grade_date = data.get('date')
        
        if not all([student_id, subject, value, grade_date]):
            return JsonResponse({'success': False, 'message': 'Не все обязательные поля заполнены'}, status=400)
        
        try:
            value = int(value)
            if value < 1 or value > 5:
                return JsonResponse({'success': False, 'message': 'Оценка должна быть от 1 до 5'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Некорректное значение оценки'}, status=400)
        
        student = get_object_or_404(CustomUser, id=student_id, user_type='student')
        
        try:
            grade_date_obj = datetime.strptime(grade_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Некорректный формат даты. Используйте YYYY-MM-DD'}, status=400)
        
        grade = Grade.objects.create(
            student=student,
            teacher=request.user,
            subject=subject,
            value=value,
            comment=comment,
            date=grade_date_obj
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Оценка успешно добавлена',
            'grade': {
                'id': grade.id,
                'subject': grade.subject,
                'value': grade.value,
                'comment': grade.comment,
                'date': grade.date.strftime('%d.%m.%Y'),
                'teacher_name': request.user.get_full_name() or request.user.username,
                'created_at': grade.created_at.strftime('%d.%m.%Y %H:%M')
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        print(f"Ошибка при добавлении оценки: {e}")
        return JsonResponse({'success': False, 'message': f'Ошибка сервера: {str(e)}'}, status=500)

@csrf_exempt
@require_POST
@login_required
def mark_attendance_api(request):
    if request.user.user_type != 'teacher':
        return JsonResponse({'success': False, 'message': 'Доступ запрещен'}, status=403)
    
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        subject = data.get('subject')
        status = data.get('status')
        attendance_date = data.get('date')
        
        if not all([student_id, subject, status, attendance_date]):
            return JsonResponse({'success': False, 'message': 'Не все обязательные поля заполнены'}, status=400)
        
        if status not in ['present', 'absent', 'late']:
            return JsonResponse({'success': False, 'message': 'Некорректный статус посещаемости'}, status=400)
        
        student = get_object_or_404(CustomUser, id=student_id, user_type='student')
        
        try:
            attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Некорректный формат даты. Используйте YYYY-MM-DD'}, status=400)
        
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            subject=subject,
            date=attendance_date_obj,
            defaults={
                'teacher': request.user,
                'status': status
            }
        )
        
        if not created:
            attendance.teacher = request.user
            attendance.status = status
            attendance.save()
        
        status_text = 'Присутствовал' if status == 'present' else 'Опоздал' if status == 'late' else 'Отсутствовал'
        
        return JsonResponse({
            'success': True,
            'message': f'Посещаемость отмечена: {status_text}',
            'attendance': {
                'id': attendance.id,
                'subject': attendance.subject,
                'date': attendance.date.strftime('%d.%m.%Y'),
                'status': attendance.status,
                'status_text': status_text,
                'teacher_name': request.user.get_full_name() or request.user.username,
                'created_at': attendance.created_at.strftime('%d.%m.%Y %H:%M')
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        print(f"Ошибка при отметке посещаемости: {e}")
        return JsonResponse({'success': False, 'message': f'Ошибка сервера: {str(e)}'}, status=500)

@login_required
def get_student_details_api(request, student_id):
    if request.user.user_type != 'teacher':
        return JsonResponse({'success': False, 'message': 'Доступ запрещен'}, status=403)
    
    try:
        student = get_object_or_404(CustomUser, id=student_id, user_type='student')
        
        grades = Grade.objects.filter(student=student).select_related('teacher')
        attendance = Attendance.objects.filter(student=student).select_related('teacher')
        
        grades_data = []
        for grade in grades.order_by('-date')[:10]:
            grades_data.append({
                'subject': grade.subject,
                'value': grade.value,
                'comment': grade.comment,
                'date': grade.date.strftime('%d.%m.%Y'),
                'teacher': grade.teacher.get_full_name() or grade.teacher.username
            })
        
        attendance_stats = {
            'present': attendance.filter(status='present').count(),
            'absent': attendance.filter(status='absent').count(),
            'late': attendance.filter(status='late').count(),
            'total': attendance.count()
        }
        
        avg_grade = None
        if grades.exists():
            avg_grade = sum(g.value for g in grades) / grades.count()
        
        return JsonResponse({
            'success': True,
            'student': {
                'id': student.id,
                'username': student.username,
                'full_name': student.get_full_name(),
                'email': student.email,
                'group': student.group or 'Не указана',
                'level': student.level or 'Не указан',
                'date_joined': student.date_joined.strftime('%d.%m.%Y')
            },
            'grades': grades_data,
            'attendance_stats': attendance_stats,
            'avg_grade': avg_grade,
            'total_grades': grades.count()
        })
    
    except Exception as e:
        print(f"Ошибка при получении данных студента: {e}")
        return JsonResponse({'success': False, 'message': f'Ошибка загрузки данных: {str(e)}'}, status=500)

def create_default_schedule():
    teachers = CustomUser.objects.filter(user_type='teacher')
    if not teachers.exists():
        print("Нет преподавателей в системе для создания расписания")
        return
    
    default_schedule = [
        {'group': 'A1', 'day': 'monday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Грамматика', 'classroom': '101'},
        {'group': 'A1', 'day': 'monday', 'time_start': '11:00', 'time_end': '12:30', 'subject': 'Разговорная практика', 'classroom': '102'},
        {'group': 'A1', 'day': 'tuesday', 'time_start': '10:00', 'time_end': '11:30', 'subject': 'Словарь', 'classroom': '103'},
        {'group': 'A1', 'day': 'wednesday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Аудирование', 'classroom': '101'},
        {'group': 'A1', 'day': 'thursday', 'time_start': '16:00', 'time_end': '17:30', 'subject': 'Письмо', 'classroom': '104'},
        {'group': 'A1', 'day': 'friday', 'time_start': '13:00', 'time_end': '14:30', 'subject': 'Чтение', 'classroom': '105'},
        
        {'group': 'A2', 'day': 'monday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Бизнес-английский', 'classroom': '201'},
        {'group': 'A2', 'day': 'tuesday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Грамматика', 'classroom': '202'},
        {'group': 'A2', 'day': 'wednesday', 'time_start': '11:00', 'time_end': '12:30', 'subject': 'Разговорная практика', 'classroom': '203'},
        {'group': 'A2', 'day': 'thursday', 'time_start': '13:00', 'time_end': '14:30', 'subject': 'Письмо', 'classroom': '201'},
        {'group': 'A2', 'day': 'friday', 'time_start': '15:00', 'time_end': '16:30', 'subject': 'Аудирование', 'classroom': '204'},
        
        {'group': 'B1', 'day': 'monday', 'time_start': '16:00', 'time_end': '17:30', 'subject': 'Подготовка к IELTS', 'classroom': '301'},
        {'group': 'B1', 'day': 'tuesday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Бизнес-английский', 'classroom': '302'},
        {'group': 'B1', 'day': 'wednesday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Грамматика', 'classroom': '303'},
        {'group': 'B1', 'day': 'thursday', 'time_start': '11:00', 'time_end': '12:30', 'subject': 'Разговорный клуб', 'classroom': '301'},
        {'group': 'B1', 'day': 'friday', 'time_start': '13:00', 'time_end': '14:30', 'subject': 'Письмо', 'classroom': '304'},
        
        {'group': 'B2', 'day': 'monday', 'time_start': '10:00', 'time_end': '11:30', 'subject': 'Академическое письмо', 'classroom': '401'},
        {'group': 'B2', 'day': 'tuesday', 'time_start': '16:00', 'time_end': '17:30', 'subject': 'Деловая переписка', 'classroom': '402'},
        {'group': 'B2', 'day': 'wednesday', 'time_start': '14:00', 'time_end': '15:30', 'subject': 'Публичные выступления', 'classroom': '403'},
        {'group': 'B2', 'day': 'thursday', 'time_start': '09:00', 'time_end': '10:30', 'subject': 'Аналитическое чтение', 'classroom': '401'},
        
        {'group': 'C1', 'day': 'monday', 'time_start': '18:00', 'time_end': '19:30', 'subject': 'Профессиональный английский', 'classroom': '501'},
        {'group': 'C1', 'day': 'tuesday', 'time_start': '18:00', 'time_end': '19:30', 'subject': 'Научная литература', 'classroom': '502'},
        {'group': 'C1', 'day': 'thursday', 'time_start': '18:00', 'time_end': '19:30', 'subject': 'Переводческое дело', 'classroom': '501'},
    ]
    
    created_count = 0
    for i, lesson_data in enumerate(default_schedule):
        try:
            if 'Грамматика' in lesson_data['subject'] or 'Аудирование' in lesson_data['subject']:
                teacher = teachers.filter(username__icontains='рустам').first() or teachers.first()
            elif 'Бизнес' in lesson_data['subject'] or 'Письмо' in lesson_data['subject']:
                teacher = teachers.filter(username__icontains='андрей').first() or teachers.first()
            elif 'Разговор' in lesson_data['subject'] or 'Словарь' in lesson_data['subject']:
                teacher = teachers.filter(username__icontains='никита').first() or teachers.first()
            else:
                teacher = teachers.first()
            
            schedule, created = Schedule.objects.get_or_create(
                group=lesson_data['group'],
                day=lesson_data['day'],
                time_start=lesson_data['time_start'],
                time_end=lesson_data['time_end'],
                defaults={
                    'subject': lesson_data['subject'],
                    'teacher': teacher,
                    'classroom': lesson_data['classroom'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
        except Exception as e:
            print(f"Ошибка при создании расписания: {e}")
    
    print(f"Создано расписаний: {created_count}")