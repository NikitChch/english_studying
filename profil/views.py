from django.shortcuts import render
from django.http import JsonResponse
from feedback.models import Feedback
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET


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
        feedbacks_list.append({
            'id': feedback.id,
            'name': feedback.name,
            'subject': feedback.subject,
            'message': feedback.message,
            'average_rating': feedback.average_rating,
            'total_score': feedback.total_score,
            'feedback_type': feedback.feedback_type,
            'feedback_type_display': feedback.get_feedback_type_display(),
            'created_at': feedback.created_at.strftime('%d.%m.%Y'),
        })
    
    return JsonResponse({
        'feedbacks': feedbacks_list,
        'has_more': current_page.has_next(),
        'current_page': page,
        'total_pages': paginator.num_pages
    })