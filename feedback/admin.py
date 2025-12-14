from django.contrib import admin
from .models import Feedback
from django.utils.html import format_html
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'final_rating_display', 'sentiment_display', 'total_score_display', 'is_processed', 'created_at']
    list_filter = ['feedback_type', 'is_processed', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'processed_at', 'score_details', 'file_link', 'sentiment_analysis']
    list_editable = ['is_processed']
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'email', 'phone', 'subscribe_newsletter')
        }),
        ('Содержание отзыва', {
            'fields': ('feedback_type', 'subject', 'message', 'attach_file', 'file_link')
        }),
        ('Оценки пользователя', {
            'fields': (
                'site_design_rating', 
                'usability_rating', 
                'content_rating', 
                'speed_rating',
                'would_recommend',
                'overall_satisfaction',
                'score_details'
            )
        }),
        ('Открытые вопросы', {
            'fields': ('most_liked', 'improvements', 'suggestions', 'additional_comments'),
            'classes': ('collapse',)
        }),
        ('Анализ тональности', {
            'fields': ('comments_sentiment_score', 'sentiment_analysis'),
            'classes': ('wide',)
        }),
        ('Итоговые расчеты', {
            'fields': ('average_rating', 'total_score', 'max_possible_score'),
            'classes': ('collapse',)
        }),
        ('Статус обработки', {
            'fields': ('is_processed', 'processed_at', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        try:
            user = User.objects.filter(email=obj.email).first()
            if user:
                return format_html(
                    '<div>'
                    '<strong>{}</strong><br>'
                    '<small>{} ({})</small><br>'
                    '<small>Телефон: {}</small>'
                    '</div>',
                    obj.name,
                    obj.email,
                    user.get_user_type_display(),
                    obj.phone or 'Не указан'
                )
            else:
                return format_html(
                    '<div>'
                    '<strong>{}</strong><br>'
                    '<small>{}</small><br>'
                    '<small>Телефон: {}</small>'
                    '</div>',
                    obj.name,
                    obj.email,
                    obj.phone or 'Не указан'
                )
        except:
            return f"{obj.name} ({obj.email})"
    user_info.short_description = 'Пользователь'
    
    def final_rating_display(self, obj):
        rating = obj.get_final_site_rating()
        stars = obj.get_rating_display()
        return format_html(
            '<div style="font-size: 18px;">{} <strong>{}/5</strong></div>',
            stars,
            rating
        )
    final_rating_display.short_description = 'Итоговый рейтинг'
    
    def sentiment_display(self, obj):
        sentiment = obj.comments_sentiment_score
        color = 'success' if sentiment >= 4 else 'info' if sentiment >= 3 else 'secondary' if sentiment >= 2 else 'warning' if sentiment >= 1 else 'danger'
        emoji = '😊' if sentiment >= 4 else '🙂' if sentiment >= 3 else '😐' if sentiment >= 2 else '😕' if sentiment >= 1 else '😠'
        
        return format_html(
            '<div class="d-flex align-items-center">'
            '<span style="font-size: 1.5rem; margin-right: 8px;">{}</span>'
            '<div class="progress" style="height: 20px; width: 80px;">'
            '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;" '
            'aria-valuenow="{}" aria-valuemin="0" aria-valuemax="100">'
            '</div></div>'
            '<span style="margin-left: 8px; font-weight: bold;">{}/5</span>'
            '</div>',
            emoji, color, (sentiment / 5) * 100, (sentiment / 5) * 100, sentiment
        )
    sentiment_display.short_description = 'Тональность'
    
    def total_score_display(self, obj):
        percentage = obj.get_score_percentage()
        color = 'success' if percentage >= 80 else 'info' if percentage >= 60 else 'warning' if percentage >= 40 else 'danger'
        return format_html(
            '<div class="progress" style="height: 20px; width: 100px;">'
            '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;" '
            'aria-valuenow="{}" aria-valuemin="0" aria-valuemax="100">'
            '{}%</div></div>',
            color, percentage, percentage, int(percentage)
        )
    total_score_display.short_description = 'Результат'
    
    def score_details(self, obj):
        return format_html(
            '<div>'
            '<p><strong>Итоговый рейтинг:</strong> {} {}/5</p>'
            '<p><strong>Баллы:</strong> {} / {}</p>'
            '<p><strong>Процент:</strong> {}%</p>'
            '<p><strong>Средняя оценка:</strong> {}/5</p>'
            '<p><strong>Оценка тональности:</strong> {}/5</p>'
            '</div>',
            obj.get_rating_display(),
            obj.get_final_site_rating(),
            obj.total_score, obj.max_possible_score,
            obj.get_score_percentage(),
            obj.average_rating,
            obj.comments_sentiment_score
        )
    score_details.short_description = 'Детали оценки'
    
    def sentiment_analysis(self, obj):
        text_fields = [
            obj.message,
            obj.most_liked,
            obj.improvements,
            obj.suggestions,
            obj.additional_comments
        ]
        
        all_text = ' '.join([str(t) for t in text_fields if t])
        
        positive_words = ['хорошо', 'отлично', 'прекрасно', 'замечательно', 'супер']
        negative_words = ['плохо', 'ужасно', 'отвратительно', 'кошмар', 'ужасный']
        
        positive_count = sum([all_text.lower().count(word) for word in positive_words])
        negative_count = sum([all_text.lower().count(word) for word in negative_words])
        
        sentiment_status = "очень позитивно" if obj.comments_sentiment_score >= 4 else \
                          "позитивно" if obj.comments_sentiment_score >= 3 else \
                          "нейтрально" if obj.comments_sentiment_score >= 2 else \
                          "негативно" if obj.comments_sentiment_score >= 1 else \
                          "очень негативно"
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            '<h6>Детальный анализ тональности:</h6>'
            '<p><strong>Оценка:</strong> {}/5 ({})</p>'
            '<p><strong>Положительных слов найдено:</strong> {}</p>'
            '<p><strong>Отрицательных слов найдено:</strong> {}</p>'
            '<p><strong>Общее количество символов:</strong> {}</p>'
            '<div class="progress mt-2" style="height: 10px;">'
            '<div class="progress-bar bg-success" style="width: {}%"></div>'
            '<div class="progress-bar bg-danger" style="width: {}%"></div>'
            '</div>'
            '</div>',
            obj.comments_sentiment_score, sentiment_status,
            positive_count, negative_count, len(all_text),
            (positive_count / max(1, positive_count + negative_count)) * 100,
            (negative_count / max(1, positive_count + negative_count)) * 100
        )
    sentiment_analysis.short_description = 'Анализ тональности комментариев'
    
    def file_link(self, obj):
        if obj.attach_file:
            return format_html(
                '<a href="{}" target="_blank">📎 {}</a>',
                obj.attach_file.url,
                obj.filename()
            )
        return "Файл не прикреплен"
    file_link.short_description = 'Ссылка на файл'
    
    def mark_as_processed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_processed=True, processed_at=timezone.now())
        self.message_user(request, f"{updated} отзывов отмечены как обработанные")
    mark_as_processed.short_description = "Отметить как обработанные"
    
    def mark_as_unprocessed(self, request, queryset):
        updated = queryset.update(is_processed=False, processed_at=None)
        self.message_user(request, f"{updated} отзывов отмечены как необработанные")
    mark_as_unprocessed.short_description = "Отметить как необработанные"
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_processed:
            return self.readonly_fields + ('is_processed',)
        return self.readonly_fields