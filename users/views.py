from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, UpdateView, FormView
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, 
    PasswordChangeDoneView, PasswordResetView,
    PasswordResetDoneView, PasswordResetCompleteView
)
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from datetime import datetime

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm, PasswordResetCodeForm
from .models import CustomUser, PasswordResetCode


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Вход в систему'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = '/'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Вы успешно вышли из системы!')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(View):
    
    template_name = 'registration/register.html'
    
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {
            'form': form,
            'page_title': 'Регистрация'
        })
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('users:profile')
        
        return render(request, self.template_name, {
            'form': form,
            'page_title': 'Регистрация'
        })


class ProfileView(TemplateView):
    template_name = 'profil.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Мой профиль'
        context['user'] = self.request.user
        
        from diary.models import Schedule
        import json
        
        if self.request.user.user_type == 'student' and self.request.user.group:
            schedule_lessons = Schedule.objects.filter(
                group=self.request.user.group,
                is_active=True
            ).order_by('day', 'time_start').select_related('teacher')
            
            schedule_data = {}
            
            for lesson in schedule_lessons:
                day = lesson.get_day_display()
                if day not in schedule_data:
                    schedule_data[day] = []
                
                teacher_name = ''
                if lesson.teacher:
                    teacher_name = lesson.teacher.get_full_name()
                    if not teacher_name:
                        teacher_name = lesson.teacher.username
                
                schedule_data[day].append({
                    'time': f'{lesson.time_start.strftime("%H:%M")} - {lesson.time_end.strftime("%H:%M")}',
                    'subject': lesson.subject,
                    'teacher': teacher_name,
                    'classroom': lesson.classroom
                })
            
            context['schedule_data_json'] = json.dumps(schedule_data)
            print(f"Расписание для группы {self.request.user.group}: {len(schedule_lessons)} занятий")
        
        elif self.request.user.user_type == 'teacher':
            schedule_lessons = Schedule.objects.filter(
                teacher=self.request.user,
                is_active=True
            ).order_by('day', 'time_start')
            
            teacher_schedule_data = []
            
            for lesson in schedule_lessons:
                teacher_schedule_data.append({
                    'day': lesson.get_day_display(),
                    'time': f'{lesson.time_start.strftime("%H:%M")} - {lesson.time_end.strftime("%H:%M")}',
                    'subject': lesson.subject,
                    'group': lesson.group,
                    'classroom': lesson.classroom
                })
            
            context['teacher_schedule_json'] = json.dumps(teacher_schedule_data)
            print(f"Расписание для преподавателя {self.request.user.username}: {len(schedule_lessons)} занятий")
        
        if self.request.user.user_type == 'student':
            try:
                from courses.models import CourseOrder
                user_courses = CourseOrder.objects.filter(
                    student=self.request.user
                ).select_related('course').order_by('-order_date')
                
                context['user_courses'] = user_courses
                
                context['total_courses'] = user_courses.count()
                context['in_progress_courses'] = user_courses.filter(status='in_progress').count()
                context['completed_courses'] = user_courses.filter(status='completed').count()
                
            except Exception as e:
                print(f"Ошибка при получении курсов: {e}")
                context['user_courses'] = []
                context['total_courses'] = 0
                context['in_progress_courses'] = 0
                context['completed_courses'] = 0
        
        return context


class ProfileUpdateView(UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'profile_update.html'
    success_url = reverse_lazy('users:profile')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Редактирование профиля'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Смена пароля'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Пароль успешно изменен'
        return context


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Восстановление пароля'
        return context
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        print(f"Отправка кода восстановления пароля на: {email}")
        
        try:
            user = CustomUser.objects.get(email=email)
            
            reset_code = PasswordResetCode.generate_code(user, email)
            
            self.request.session['reset_email'] = email
            self._send_reset_email(user, reset_code.code)
            
            messages.success(
                self.request,
                f'Код восстановления отправлен на {email}. Проверьте вашу почту.'
            )
            
            return redirect('users:password_reset_code')
            
        except CustomUser.DoesNotExist:
            messages.info(
                self.request,
                f'Если email зарегистрирован, код восстановления будет отправлен на {email}'
            )
            self.request.session['reset_email'] = email
            return redirect('users:password_reset_code')
    
    def _send_reset_email(self, user, code):
        subject = render_to_string(
            self.subject_template_name,
            {'site_name': settings.SITE_NAME}
        ).strip()
        
        message = render_to_string(
            self.email_template_name,
            {
                'email': user.email,
                'site_name': settings.SITE_NAME,
                'user': user,
                'code': code,
            }
        )
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"Email с кодом {code} отправлен на {user.email}")
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
            raise


class PasswordResetCodeView(View):
    
    template_name = 'registration/password_reset_code.html'
    
    def get(self, request):
        email = request.session.get('reset_email')
        
        if not email:
            messages.error(request, 'Сначала укажите email для восстановления')
            return redirect('users:password_reset')
        
        code_used = request.session.get('code_verified', False)
        if code_used:
            del request.session['code_verified']
            storage = messages.get_messages(request)
            for message in storage:
                if 'Код восстановления отправлен' in str(message):
                    storage.used = True
        
        form = PasswordResetCodeForm(initial={'email': email})
        
        can_resend = True
        time_left = 0
        
        if 'last_resend_time' in request.session:
            can_resend = self.can_resend_code(request)
            time_left = self.get_resend_time_left(request)
        
        context = {
            'form': form,
            'email': email,
            'can_resend': can_resend,
            'page_title': 'Введите код подтверждения',
            'time_left': time_left,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        email = request.session.get('reset_email')
        
        if not email:
            messages.error(request, 'Сессия истекла. Пожалуйста, начните заново.')
            return redirect('users:password_reset')
        
        form = PasswordResetCodeForm({'email': email, 'code': request.POST.get('code', '')})
        
        if form.is_valid():
            code = form.cleaned_data['code']
            
            reset_code = PasswordResetCode.validate_code(email, code)
            
            if reset_code:
                reset_code.mark_as_used()
                
                request.session['code_verified'] = True
                request.session['reset_user_id'] = reset_code.user.id
                
                storage = messages.get_messages(request)
                for message in storage:
                    if 'Код восстановления отправлен' in str(message):
                        storage.used = True
                
                messages.success(request, 'Код подтвержден! Теперь установите новый пароль.')
                return redirect('users:password_reset_confirm')
            else:
                messages.error(request, 'Неверный код или срок его действия истек.')
        else:
            messages.error(request, 'Неверный формат кода. Введите 6 цифр.')
        
        can_resend = True
        time_left = 0
        if 'last_resend_time' in request.session:
            can_resend = self.can_resend_code(request)
            time_left = self.get_resend_time_left(request)
        
        context = {
            'form': form,
            'email': email,
            'can_resend': can_resend,
            'page_title': 'Введите код подтверждения',
            'time_left': time_left,
        }
        
        return render(request, self.template_name, context)
    
    def can_resend_code(self, request):
        last_sent = request.session.get('last_resend_time')
        if not last_sent:
            return True
        
        last_sent_dt = datetime.fromisoformat(last_sent)
        time_passed = (datetime.now() - last_sent_dt).total_seconds()
        
        return time_passed >= 30
    
    def get_resend_time_left(self, request):
        last_sent = request.session.get('last_resend_time')
        if not last_sent:
            return 0
        
        last_sent_dt = datetime.fromisoformat(last_sent)
        time_passed = (datetime.now() - last_sent_dt).total_seconds()
        
        return max(0, 30 - int(time_passed))

class ResendResetCodeView(View):
    
    def post(self, request):
        email = request.session.get('reset_email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Сессия истекла'
            }, status=400)
        
        view = PasswordResetCodeView()
        if not view.can_resend_code(request):
            time_left = view.get_resend_time_left(request)
            return JsonResponse({
                'success': False,
                'message': f'Повторная отправка будет доступна через {time_left} секунд'
            }, status=429)
        
        try:
            user = CustomUser.objects.get(email=email)
            
            reset_code = PasswordResetCode.generate_code(user, email)
            
            send_mail(
                subject=f'Новый код восстановления для {settings.SITE_NAME}',
                message=f'Ваш новый код восстановления: {reset_code.code}\n\n'
                       f'Код действителен в течение 30 минут.\n'
                       f'Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            request.session['last_resend_time'] = datetime.now().isoformat()
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Новый код отправлен на вашу почту'
            })
            
        except CustomUser.DoesNotExist:
            request.session['last_resend_time'] = datetime.now().isoformat()
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Если email зарегистрирован, новый код отправлен'
            })
        except Exception as e:
            print(f"Ошибка при повторной отправке кода: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Ошибка отправки: {str(e)}'
            }, status=500)


class CustomPasswordResetConfirmView(FormView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('code_verified'):
            messages.error(request, 'Сначала подтвердите код восстановления')
            return redirect('users:password_reset_code')
        
        user_id = request.session.get('reset_user_id')
        if not user_id:
            messages.error(request, 'Сессия истекла. Пожалуйста, начните заново.')
            return redirect('users:password_reset')
        
        try:
            self.user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
            return redirect('users:password_reset')
        
        storage = messages.get_messages(request)
        for message in storage:
            if 'Код восстановления отправлен' in str(message):
                storage.used = True
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Введите новый пароль'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs
    
    def form_valid(self, form):
        user = form.save()
        
        update_session_auth_hash(self.request, user)
        
        messages.success(
            self.request,
            'Пароль успешно изменен! Теперь вы можете войти с новым паролем.'
        )
        
        session_keys = ['reset_email', 'code_verified', 'reset_user_id', 'last_resend_time']
        for key in session_keys:
            if key in self.request.session:
                del self.request.session[key]
        
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Пароль восстановлен'
        return context


@csrf_exempt
def send_test_email_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email адрес не указан'
                }, status=400)
            
            try:
                send_mail(
                    subject='Тестовое письмо с English Studying Platform',
                    message=f'''Поздравляем! Настройки email работают корректно.

Отправитель: {settings.DEFAULT_FROM_EMAIL}
Получатель: {email}
Хост: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}

Это тестовое письмо от системы восстановления пароля.
Если вы видите это письмо, значит восстановление пароля будет работать.

С уважением,
Команда {settings.SITE_NAME}''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Тестовое письмо успешно отправлено на {email}. Проверьте вашу почту (и папку "Спам").'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Ошибка отправки: {str(e)}'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Неверный формат данных'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Метод не разрешен'
    }, status=405)