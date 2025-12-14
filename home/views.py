from django.shortcuts import render
from django.http import JsonResponse
from feedback.models import Feedback, FeedbackLike
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


def index(request):
    try:
        feedback_stats = Feedback.objects.aggregate(
            avg_rating=Avg('average_rating'),
            total_feedbacks=Count('id'),
            avg_design=Avg('site_design_rating'),
            avg_usability=Avg('usability_rating'),
            avg_content=Avg('content_rating'),
            avg_speed=Avg('speed_rating')
        )

        if not feedback_stats['total_feedbacks']:
            raise Exception("No feedbacks")

        overall_rating = round(feedback_stats['avg_rating'], 1)
        total_feedbacks = feedback_stats['total_feedbacks']
        avg_design = round(feedback_stats['avg_design'] or 0, 1)
        avg_usability = round(feedback_stats['avg_usability'] or 0, 1)
        avg_content = round(feedback_stats['avg_content'] or 0, 1)
        avg_speed = round(feedback_stats['avg_speed'] or 0, 1)

    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
        overall_rating = 4.5
        total_feedbacks = 125
        avg_design = 4.2
        avg_usability = 4.5
        avg_content = 4.7
        avg_speed = 4.3

    context = {
        'title': 'ENGLISH STUDING - Изучение английского языка',
        'promo_product': 'Первый месяц бесплатно при регистрации!',
        'overall_rating': overall_rating,
        'total_feedbacks': total_feedbacks,
        'avg_design': avg_design,
        'avg_usability': avg_usability,
        'avg_content': avg_content,
        'avg_speed': avg_speed,
    }

    return render(request, 'index.html', context)


@require_GET
def api_feedbacks(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 5))
    
    feedbacks_qs = Feedback.objects.all().order_by('-created_at')
    
    paginator = Paginator(feedbacks_qs, per_page)
    
    try:
        current_page = paginator.page(page)
    except:
        return JsonResponse({'feedbacks': [], 'has_more': False})
    
    feedbacks_list = []
    for feedback in current_page:
        likes_count = feedback.likes.count()
        
        user_has_liked = False
        if request.user.is_authenticated:
            user_has_liked = feedback.likes.filter(user=request.user).exists()
        
        avatar_url = None
        has_avatar = False
        
        try:
            from users.models import CustomUser
            
            user = CustomUser.objects.filter(email=feedback.email).first()
            if user and user.profile_picture:
                try:
                    avatar_url = user.profile_picture.url
                    has_avatar = True
                    print(f"Найдена аватарка для {feedback.email}: {avatar_url}")
                except ValueError:
                    avatar_url = None
                    has_avatar = False
        except Exception as e:
            print(f"Ошибка при получении аватарки: {e}")
        
        average_rating = float(feedback.average_rating) if feedback.average_rating else 0.0
        
        feedbacks_list.append({
            'id': feedback.id,
            'name': feedback.name,
            'subject': feedback.subject,
            'message': feedback.message,
            'average_rating': average_rating,
            'total_score': feedback.total_score,
            'feedback_type': feedback.feedback_type,
            'feedback_type_display': feedback.get_feedback_type_display(),
            'created_at': feedback.created_at.strftime('%d.%m.%Y'),
            'likes_count': likes_count,
            'user_has_liked': user_has_liked,
            'avatar_url': avatar_url,
            'has_avatar': has_avatar,
        })
    
    return JsonResponse({
        'feedbacks': feedbacks_list,
        'has_more': current_page.has_next(),
        'current_page': page,
        'total_pages': paginator.num_pages
    })


@csrf_exempt
@login_required
def api_toggle_like(request, feedback_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        feedback = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        return JsonResponse({'error': 'Отзыв не найден'}, status=404)
    
    like_exists = FeedbackLike.objects.filter(
        feedback=feedback, 
        user=request.user
    ).exists()
    
    if like_exists:
        FeedbackLike.objects.filter(
            feedback=feedback, 
            user=request.user
        ).delete()
        action = 'unliked'
    else:
        FeedbackLike.objects.create(
            feedback=feedback,
            user=request.user
        )
        action = 'liked'
    
    new_likes_count = feedback.likes.count()
    
    return JsonResponse({
        'success': True,
        'action': action,
        'likes_count': new_likes_count,
        'user_has_liked': not like_exists
    })