from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Count
from .forms import FeedbackForm
from .models import Feedback
import logging

logger = logging.getLogger('feedback')

class FeedbackView(View):
    template_name = 'feedback/feedback_form.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': request.user.phone or '',
            }
            form = FeedbackForm(initial=initial_data)
        else:
            form = FeedbackForm()
        
        overall_stats = Feedback.objects.aggregate(
            avg_rating=Avg('average_rating'),
            total_feedbacks=Count('id'),
            avg_design=Avg('site_design_rating'),
            avg_usability=Avg('usability_rating'),
            avg_content=Avg('content_rating'),
            avg_speed=Avg('speed_rating'),
            avg_sentiment=Avg('comments_sentiment_score')
        )
        
        context = {
            'form': form,
            'user': request.user,
            'is_authenticated': request.user.is_authenticated,
            'site_overall_rating': round(overall_stats['avg_rating'] or 0, 1) if overall_stats['avg_rating'] else 4.5,
            'site_total_feedbacks': overall_stats['total_feedbacks'] or 125,
            'site_avg_sentiment': round(overall_stats['avg_sentiment'] or 0, 1) if overall_stats['avg_sentiment'] else 2.5,
            'current_rating': 0,
            'current_score': 0,
        }
        
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'Для отправки отзыва необходимо авторизоваться.')
            return redirect('users:login')
            
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                feedback = form.save(commit=False)
                
                feedback.name = request.user.get_full_name() or request.user.username
                feedback.email = request.user.email
                feedback.phone = request.user.phone or ''
                
                feedback.comments_sentiment_score = feedback.calculate_comments_sentiment()
                feedback.total_score = feedback.calculate_total_score()
                feedback.max_possible_score = feedback.calculate_max_possible_score()
                feedback.average_rating = feedback.calculate_average_rating()
                feedback.save()
                
                final_rating = feedback.get_final_site_rating()
                score_percentage = feedback.get_score_percentage()
                
                request.session['feedback_result'] = {
                    'final_rating': final_rating,
                    'score_percentage': score_percentage,
                    'total_score': feedback.total_score,
                    'max_score': feedback.max_possible_score,
                    'average_rating': feedback.average_rating,
                    'comments_sentiment': feedback.comments_sentiment_score,
                }
                
                self.send_notification_email(feedback)
                
                messages.success(request, 'Ваше сообщение успешно отправлено! Спасибо за вашу обратную связь.')
                return redirect('feedback:success')
                
            except Exception as e:
                logger.error(f"Ошибка сохранения отзыва: {e}")
                messages.error(request, f'Произошла ошибка при сохранении: {e}')
        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
        
        context = {
            'form': form,
            'user': request.user,
            'is_authenticated': request.user.is_authenticated,
        }
        return render(request, self.template_name, context)

    def send_notification_email(self, feedback):
        try:
            logger.info(f"Начало отправки email для отзыва #{feedback.id}")
            
            subject = f'Новое обращение с рейтингом {feedback.get_final_site_rating():.1f}/5'
            
            sentiment_score = feedback.comments_sentiment_score
            sentiment_status = "очень негативно" if sentiment_score < 1 else \
                              "негативно" if sentiment_score < 2 else \
                              "нейтрально" if sentiment_score < 3 else \
                              "позитивно" if sentiment_score < 4 else \
                              "очень позитивно"
            
            text_fields = [
                feedback.message,
                feedback.most_liked,
                feedback.improvements,
                feedback.suggestions,
                feedback.additional_comments
            ]
            
            all_text = ' '.join([str(t) for t in text_fields if t]).lower()
            
            POSITIVE_WORDS = [
                'хорошо', 'отлично', 'прекрасно', 'замечательно', 'супер', 'отличный',
                'понравилось', 'нравится', 'удобно', 'понятно', 'легко', 'просто',
                'быстро', 'эффективно', 'полезно', 'интересно', 'класс', 'великолепно'
            ]
            
            NEGATIVE_WORDS = [
                'плохо', 'ужасно', 'отвратительно', 'кошмар', 'ужасный', 'плохой',
                'неудобно', 'непонятно', 'сложно', 'запутанно', 'медленно', 'тормозит',
                'глючит', 'баги', 'ошибки', 'не работает', 'сломалось', 'неправильно'
            ]
            
            positive_count = sum([all_text.count(word) for word in POSITIVE_WORDS])
            negative_count = sum([all_text.count(word) for word in NEGATIVE_WORDS])
            
            message = f'''
Поступило новое обращение через форму обратной связи:

ИД: #{feedback.id}
Тип: {feedback.get_feedback_type_display()}
Имя: {feedback.name}
Email: {feedback.email}
Телефон: {feedback.phone or 'Не указан'}

ИТОГОВЫЙ РЕЙТИНГ САЙТА: {feedback.get_final_site_rating():.1f}/5
{feedback.get_rating_display()}
Набрано баллов: {feedback.total_score}/{feedback.max_possible_score} ({feedback.get_score_percentage():.1f}%)

--- АНАЛИЗ ТОНАЛЬНОСТИ ---
Оценка тональности: {sentiment_score:.1f}/5 ({sentiment_status})
Положительных слов: {positive_count}
Отрицательных слов: {negative_count}

--- РЕЙТИНГОВЫЕ ВОПРОСЫ ---
Дизайн сайта: {feedback.site_design_rating}/5
Удобство использования: {feedback.usability_rating}/5
Качество контента: {feedback.content_rating}/5
Скорость работы: {feedback.speed_rating}/5

--- ВОПРОСЫ С ВЫБОРОМ ---
Порекомендуете друзьям: {feedback.get_would_recommend_display() or 'Не указано'}
Общая удовлетворенность: {feedback.get_overall_satisfaction_display() or 'Не указано'}

--- ОТКРЫТЫЕ ВОПРОСЫ ---
Что понравилось: {feedback.most_liked or 'Не указано'}
Что улучшить: {feedback.improvements or 'Не указано'}
Предложения: {feedback.suggestions or 'Не указано'}

Сообщение пользователя:
{feedback.message[:500]}{'...' if len(feedback.message) > 500 else ''}

Дата: {feedback.created_at.strftime("%d.%m.%Y %H:%M")}
            '''
            
            logger.info(f"Отправка email: subject={subject}, to={settings.ADMIN_EMAIL}")
            logger.info(f"Настройки SMTP: host={settings.EMAIL_HOST}, port={settings.EMAIL_PORT}")
            logger.info(f"Отправитель: {settings.DEFAULT_FROM_EMAIL}")
            
            result = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            
            logger.info(f"Email отправлен успешно. Результат: {result}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки email: {str(e)}", exc_info=True)
            logger.error(f"EMAIL_HOST: {settings.EMAIL_HOST}")
            logger.error(f"EMAIL_PORT: {settings.EMAIL_PORT}")
            logger.error(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            return False

class FeedbackSuccessView(LoginRequiredMixin, View):
    template_name = 'feedback/feedback_success.html'
    login_url = '/users/login/'
    redirect_field_name = 'next'
    
    def get(self, request):
        feedback_result = request.session.get('feedback_result', {})
        
        if not feedback_result:
            messages.warning(request, 'Нет данных об отправленной оценке. Заполните форму.')
            return redirect('feedback:feedback')
        
        final_rating = feedback_result.get('final_rating', 0)
        
        overall_stats = Feedback.objects.aggregate(
            avg_rating=Avg('average_rating'),
            total_feedbacks=Count('id'),
            avg_sentiment=Avg('comments_sentiment_score')
        )
        
        context = {
            'user': request.user,
            'is_authenticated': request.user.is_authenticated,
            'final_rating': round(final_rating, 1),
            'score_percentage': feedback_result.get('score_percentage', 0),
            'total_score': feedback_result.get('total_score', 0),
            'max_score': feedback_result.get('max_score', 160),
            'average_rating': feedback_result.get('average_rating', 0),
            'comments_sentiment': feedback_result.get('comments_sentiment', 0),
            
            'site_overall_rating': round(overall_stats['avg_rating'] or 0, 1) if overall_stats['avg_rating'] else 4.5,
            'site_total_feedbacks': overall_stats['total_feedbacks'] or 125,
            'site_avg_sentiment': round(overall_stats['avg_sentiment'] or 0, 1) if overall_stats['avg_sentiment'] else 2.5,
        }
        
        if 'feedback_result' in request.session:
            del request.session['feedback_result']
        
        return render(request, self.template_name, context)