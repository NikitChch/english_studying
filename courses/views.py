from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
from django.db import models
from django.core.paginator import Paginator
from django.db import transaction
import json

from .models import Course, CourseOrder, CourseModule
from .forms import CourseEnrollForm, CourseCompleteForm, CourseCreateForm, CourseEditForm, ModuleFormSet

def course_list(request):
    courses = Course.objects.filter(
        current_students__lt=models.F('max_students')
    ).order_by('start_date')
    
    level = request.GET.get('level')
    if level:
        courses = courses.filter(level=level)
    
    search = request.GET.get('search')
    if search:
        courses = courses.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'page_title': 'Курсы английского языка',
        'courses': courses,
        'levels': Course.LEVEL_CHOICES,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    is_enrolled = False
    user_order = None
    if request.user.is_authenticated:
        user_order = CourseOrder.objects.filter(
            course=course,
            student=request.user
        ).first()
        is_enrolled = user_order is not None
    
    modules = course.modules.all().order_by('order')
    
    context = {
        'page_title': course.name,
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'user_order': user_order,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def my_courses(request):
    orders = CourseOrder.objects.filter(
        student=request.user
    ).select_related('course').order_by('-order_date')
    
    total_courses = orders.count()
    completed_courses = orders.filter(status='completed').count()
    in_progress_courses = orders.filter(status='in_progress').count()
    pending_courses = orders.filter(status='pending').count()
    cancelled_courses = orders.filter(status='cancelled').count()
    
    context = {
        'page_title': 'Мои курсы',
        'orders': orders,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses,
        'pending_courses': pending_courses,
        'cancelled_courses': cancelled_courses,
    }
    return render(request, 'courses/my_courses.html', context)


@login_required
def course_enroll(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if CourseOrder.objects.filter(course=course, student=request.user).exists():
        messages.warning(request, 'Вы уже записаны на этот курс!')
        return redirect('courses:course_detail', pk=pk)
    
    if not course.is_available():
        messages.error(request, 'Курс недоступен для записи. Все места заняты.')
        return redirect('courses:course_detail', pk=pk)
    
    if request.method == 'POST':
        form = CourseEnrollForm(request.POST)
        if form.is_valid():
            order = CourseOrder(
                course=course,
                student=request.user,
                price_paid=course.price,
                status='paid',
                start_date=timezone.now().date(),
                expected_end_date=course.end_date,
            )
            order.save()
            
            course.current_students += 1
            course.save()
            
            messages.success(request, 'Вы успешно записались на курс!')
            return redirect('courses:my_courses')
    else:
        form = CourseEnrollForm()
    
    context = {
        'page_title': f'Запись на курс: {course.name}',
        'course': course,
        'form': form,
    }
    return render(request, 'courses/course_enroll.html', context)


@login_required
def course_student_detail(request, order_id):
    order = get_object_or_404(CourseOrder, id=order_id, student=request.user)
    
    if order.status == 'paid' and order.progress > 0:
        order.status = 'in_progress'
        order.save()
    
    modules = order.course.modules.all().order_by('order')
    
    completed_module_ids = order.completed_modules.values_list('id', flat=True)
    
    if order.total_modules_count > 0:
        calculated_progress = order.calculate_progress()
        if order.progress != calculated_progress:
            order.progress = calculated_progress
            order.save()
    
    context = {
        'page_title': f'Курс: {order.course.name}',
        'order': order,
        'modules': modules,
        'course': order.course,
        'completed_module_ids': list(completed_module_ids),
    }
    return render(request, 'courses/course_student_detail.html', context)


@login_required
def cancel_course(request, order_id):
    order = get_object_or_404(CourseOrder, id=order_id, student=request.user)
    
    if not order.can_be_cancelled():
        messages.error(request, 'Этот курс нельзя отменить.')
        return redirect('courses:course_student_detail', order_id=order_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        confirm_cancel = request.POST.get('confirm_cancel', False)
        
        if not confirm_cancel:
            messages.error(request, 'Вы должны подтвердить отмену курса.')
            return redirect('courses:cancel_course', order_id=order_id)
        
        try:
            with transaction.atomic():
                if order.cancel_order(reason=reason):
                    messages.success(request, 'Курс успешно отменен!')
                    
                    if reason:
                        messages.info(request, f'Причина отмены: {reason}')
                else:
                    messages.error(request, 'Не удалось отменить курс.')
                
                return redirect('courses:my_courses')
        except Exception as e:
            messages.error(request, f'Ошибка при отмене курса: {str(e)}')
            return redirect('courses:course_student_detail', order_id=order_id)
    
    context = {
        'page_title': 'Отмена курса',
        'order': order,
        'course': order.course,
    }
    return render(request, 'courses/cancel_course.html', context)


@login_required
def delete_course(request, order_id):
    order = get_object_or_404(CourseOrder, id=order_id, student=request.user)
    
    if not order.can_be_deleted():
        messages.error(request, 'Этот курс нельзя удалить.')
        return redirect('courses:my_courses')
    
    if request.method == 'POST':
        try:
            course_name = order.course.name
            order.delete()
            messages.success(request, f'Запись о курсе "{course_name}" успешно удалена.')
            return redirect('courses:my_courses')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении курса: {str(e)}')
            return redirect('courses:my_courses')
    
    context = {
        'page_title': 'Удаление записи о курсе',
        'order': order,
        'course': order.course,
    }
    return render(request, 'courses/delete_course.html', context)


@login_required
def mark_module_complete(request, order_id, module_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(CourseOrder, id=order_id, student=request.user)
            module = get_object_or_404(CourseModule, id=module_id, course=order.course)
            
            if order.completed_modules.filter(id=module_id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Этот модуль уже пройден'
                })
            
            order.completed_modules.add(module)
            
            order.progress = order.calculate_progress()
            
            if order.progress > 0 and order.status == 'paid':
                order.status = 'in_progress'
            
            order.save()
            
            return JsonResponse({
                'success': True,
                'progress': order.progress,
                'completed_modules': order.completed_modules_count,
                'total_modules': order.total_modules_count,
                'message': f'Модуль "{module.title}" отмечен как пройденный'
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'}, status=405)


@login_required
def complete_course(request, order_id):
    order = get_object_or_404(CourseOrder, id=order_id, student=request.user)
    
    if order.status == 'completed':
        messages.info(request, 'Этот курс уже завершен.')
        return redirect('courses:course_student_detail', order_id=order_id)
    
    if order.completed_modules_count < order.total_modules_count:
        messages.warning(request, 'Вы должны пройти все модули перед завершением курса!')
        return redirect('courses:course_student_detail', order_id=order_id)
    
    if order.progress < 100:
        messages.warning(request, 'Прогресс должен быть 100% для завершения курса!')
        return redirect('courses:course_student_detail', order_id=order_id)
    
    if request.method == 'POST':
        form = CourseCompleteForm(request.POST)
        if form.is_valid():
            order.status = 'completed'
            order.actual_end_date = timezone.now().date()
            order.progress = 100
            
            order.rating = int(form.cleaned_data['rating'])
            order.feedback = form.cleaned_data.get('feedback', '')
            order.save()
            
            messages.success(request, 'Курс успешно завершен! Спасибо за отзыв.')
            return redirect('courses:course_student_detail', order_id=order_id)
    else:
        form = CourseCompleteForm()
    
    context = {
        'page_title': 'Завершение курса',
        'order': order,
        'form': form,
    }
    return render(request, 'courses/complete_course.html', context)


@login_required
def update_progress(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(CourseOrder, id=order_id, student=request.user)
            progress = int(request.POST.get('progress', 0))
            
            progress = max(0, min(100, progress))
            
            total_modules = order.course.modules.count()
            if total_modules > 0:
                modules_to_complete = round((progress / 100) * total_modules)
                modules_to_complete = min(modules_to_complete, total_modules)
                
                all_modules = order.course.modules.all().order_by('order')
                
                order.completed_modules.clear()
                
                for i in range(modules_to_complete):
                    if i < len(all_modules):
                        order.completed_modules.add(all_modules[i])
            
            order.progress = progress
            
            if progress > 0 and order.status == 'paid':
                order.status = 'in_progress'
            
            order.save()
            
            return JsonResponse({
                'success': True,
                'progress': order.progress,
                'completed_modules': order.completed_modules_count,
                'total_modules': total_modules,
                'message': 'Прогресс обновлен'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'}, status=405)


@login_required
def teacher_courses(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Эта страница доступна только преподавателям')
        return redirect('users:profile')
    
    courses = Course.objects.filter(teacher=request.user).order_by('-start_date')
    
    total_courses = courses.count()
    total_students = sum(course.current_students for course in courses)
    total_income = sum(course.current_students * course.price for course in courses)
    
    context = {
        'page_title': 'Мои курсы (Преподаватель)',
        'courses': courses,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_income': total_income,
    }
    return render(request, 'courses/teacher_courses.html', context)


@login_required
def create_course(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Эта страница доступна только преподавателям')
        return redirect('users:profile')
    
    if request.method == 'POST':
        form = CourseCreateForm(request.POST, teacher=request.user)
        if form.is_valid():
            course = form.save()
            
            messages.success(request, f'Курс "{course.name}" успешно создан! Теперь добавьте модули.')
            return redirect('courses:add_modules', pk=course.id)
    else:
        form = CourseCreateForm(teacher=request.user)
    
    context = {
        'page_title': 'Создание нового курса',
        'form': form,
    }
    return render(request, 'courses/create_course.html', context)


@login_required
def add_modules(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if course.teacher != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого курса')
        return redirect('courses:teacher_courses')
    
    if request.method == 'POST':
        formset = ModuleFormSet(request.POST, instance=course)
        if formset.is_valid():
            formset.save()
            messages.success(request, f'Модули для курса "{course.name}" успешно добавлены!')
            return redirect('courses:teacher_courses')
    else:
        formset = ModuleFormSet(instance=course)
    
    context = {
        'page_title': f'Добавление модулей: {course.name}',
        'course': course,
        'formset': formset,
    }
    return render(request, 'courses/add_modules.html', context)


@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if course.teacher != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого курса')
        return redirect('courses:teacher_courses')
    
    if request.method == 'POST':
        form = CourseEditForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Курс "{course.name}" успешно обновлен!')
            return redirect('courses:teacher_courses')
    else:
        form = CourseEditForm(instance=course)
    
    context = {
        'page_title': f'Редактирование курса: {course.name}',
        'course': course,
        'form': form,
    }
    return render(request, 'courses/edit_course.html', context)


@login_required
def delete_course_teacher(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if course.teacher != request.user:
        messages.error(request, 'У вас нет прав для удаления этого курса')
        return redirect('courses:teacher_courses')
    
    if course.orders.filter(status__in=['in_progress', 'paid']).exists():
        messages.error(request, 'Нельзя удалить курс с активными студентами')
        return redirect('courses:teacher_courses')
    
    if request.method == 'POST':
        course_name = course.name
        course.delete()
        messages.success(request, f'Курс "{course_name}" успешно удален!')
        return redirect('courses:teacher_courses')
    
    context = {
        'page_title': f'Удаление курса: {course.name}',
        'course': course,
    }
    return render(request, 'courses/delete_course_teacher.html', context)


@login_required
def course_students(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if course.teacher != request.user:
        messages.error(request, 'У вас нет прав для просмотра студентов этого курса')
        return redirect('courses:teacher_courses')
    
    orders = CourseOrder.objects.filter(
        course=course
    ).select_related('student').order_by('-order_date')
    
    status_stats = {}
    for status_code, status_name in CourseOrder.STATUS_CHOICES:
        count = orders.filter(status=status_code).count()
        status_stats[status_code] = {
            'name': status_name,
            'count': count
        }
    
    context = {
        'page_title': f'Студенты курса: {course.name}',
        'course': course,
        'orders': orders,
        'status_stats': status_stats,
        'total_students': orders.count(),
        'active_students': orders.filter(status__in=['in_progress', 'paid']).count(),
        'completed_students': orders.filter(status='completed').count(),
        'total_income': course.total_income,
    }
    return render(request, 'courses/course_students.html', context)


@login_required
def teacher_course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if course.teacher != request.user:
        messages.error(request, 'У вас нет прав для просмотра этого курса')
        return redirect('courses:teacher_courses')
    
    modules = course.modules.all().order_by('order')
    orders = course.orders.all()
    
    avg_progress = 0
    if orders.exists():
        total_progress = sum(order.progress for order in orders)
        avg_progress = round(total_progress / orders.count(), 1)
    
    context = {
        'page_title': f'Курс: {course.name} (Преподаватель)',
        'course': course,
        'modules': modules,
        'orders_count': orders.count(),
        'avg_progress': avg_progress,
        'completed_count': orders.filter(status='completed').count(),
        'in_progress_count': orders.filter(status='in_progress').count(),
        'pending_count': orders.filter(status__in=['pending', 'paid']).count(),
        'cancelled_count': orders.filter(status='cancelled').count(),
        'total_income': course.total_income,
    }
    return render(request, 'courses/teacher_course_detail.html', context)


@login_required
def teacher_courses(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Эта страница доступна только преподавателям')
        return redirect('users:profile')
    
    courses = Course.objects.filter(teacher=request.user).order_by('-start_date')
    
    total_courses = courses.count()
    total_students = sum(course.current_students for course in courses)
    total_income = sum(course.total_income for course in courses)
    
    context = {
        'page_title': 'Мои курсы (Преподаватель)',
        'courses': courses,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_income': total_income,
    }
    return render(request, 'courses/teacher_courses.html', context)