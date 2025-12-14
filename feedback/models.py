from django.db import models
import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('general', 'Общий вопрос'),
        ('technical', 'Техническая проблема'),
        ('suggestion', 'Предложение по улучшению'),
        ('other', 'Другое'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Имя пользователя", blank=True)
    email = models.EmailField(verbose_name="Email адрес", blank=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    feedback_type = models.CharField(
        max_length=20, 
        choices=FEEDBACK_TYPES, 
        default='general',
        verbose_name="Тип отзыва"
    )
    
    subject = models.CharField(max_length=200, verbose_name="Тема отзыва")
    message = models.TextField(verbose_name="Текст отзыва")
    
    site_design_rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Оценка дизайна сайта"
    )
    usability_rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Оценка удобства использования"
    )
    content_rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Оценка качества контента"
    )
    speed_rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Оценка скорости работы"
    )
    
    WOULD_RECOMMEND_CHOICES = [
        ('definitely', 'Определенно да'),
        ('probably', 'Вероятно да'),
        ('not_sure', 'Не уверен'),
        ('probably_not', 'Вероятно нет'),
        ('definitely_not', 'Определенно нет'),
    ]
    
    SATISFACTION_CHOICES = [
        ('very_satisfied', 'Полностью доволен'),
        ('satisfied', 'Доволен'),
        ('neutral', 'Нейтрально'),
        ('unsatisfied', 'Не доволен'),
        ('very_unsatisfied', 'Совсем не доволен'),
    ]
    
    would_recommend = models.CharField(
        max_length=20,
        choices=WOULD_RECOMMEND_CHOICES,
        blank=True,
        verbose_name="Порекомендуете ли вы наш сайт друзьям?"
    )
    
    overall_satisfaction = models.CharField(
        max_length=20,
        choices=SATISFACTION_CHOICES,
        blank=True,
        verbose_name="Общая удовлетворенность сервисом"
    )
    
    most_liked = models.TextField(blank=True, verbose_name="Что больше всего понравилось?")
    improvements = models.TextField(blank=True, verbose_name="Что можно улучшить?")
    suggestions = models.TextField(blank=True, verbose_name="Ваши предложения")
    additional_comments = models.TextField(blank=True, verbose_name="Дополнительные комментарии")
    
    average_rating = models.FloatField(default=0, verbose_name="Средний рейтинг")
    total_score = models.IntegerField(default=0, verbose_name="Общий балл")
    max_possible_score = models.IntegerField(default=0, verbose_name="Максимально возможный балл")
    comments_sentiment_score = models.FloatField(default=0, verbose_name="Оценка тональности комментариев")
    
    subscribe_newsletter = models.BooleanField(
        default=False,
        verbose_name="Подписаться на рассылку"
    )
    attach_file = models.FileField(
        upload_to='feedback_attachments/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Прикрепленный файл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата обработки")
    admin_notes = models.TextField(blank=True, verbose_name="Заметки администратора")

    def __str__(self):
        return f"#{self.id} {self.name} - {self.subject}"

    def analyze_comments_sentiment(self):
        POSITIVE_WORDS = [
            'хорошо', 'отлично', 'прекрасно', 'замечательно', 'супер', 'отличный',
            'понравилось', 'нравится', 'удобно', 'понятно', 'легко', 'просто',
            'быстро', 'эффективно', 'полезно', 'интересно', 'класс', 'великолепно',
            'восхитительно', 'приятно', 'удобный', 'понятный', 'качественный',
            'интуитивный', 'современный', 'красивый', 'стильный', 'надежный',
            'рад', 'радость', 'счастлив', 'доволен', 'удовлетворен', 'впечатлен',
            'восторг', 'восхищение', 'удовольствие', 'наслаждение', 'увлечение',
            'комфортно', 'комфортный', 'эргономично', 'практично', 'функционально',
            'доступно', 'наглядно', 'логично', 'организовано', 'профессиональный',
            'высококачественный', 'стабильный', 'безопасный', 'точный', 'корректный',
            'грамотный', 'результативный', 'продуктивный', 'эстетичный',
            'привлекательный', 'яркий', 'красочный', 'инновационный', 'оригинальный',
            'мгновенно', 'оперативно', 'молниеносно', 'рекомендую', 'советую',
            'помогло', 'увлекательно', 'блестяще', 'гениально', 'шикарно',
            'безупречно', 'идеально', 'здорово', 'круто', 'превосходно',
            'спасибо', 'благодарю', 'отличная работа', 'молодцы', 'так держать',
            'суперский', 'потрясающе', 'обалденно', 'невероятно', 'фантастически',
            'люблю', 'обожаю', 'нравится', 'симпатичный', 'замечательный'
        ]
        
        NEGATIVE_WORDS = [
            'плохо', 'ужасно', 'отвратительно', 'кошмар', 'ужасный', 'плохой',
            'неудобно', 'непонятно', 'сложно', 'запутанно', 'медленно', 'тормозит',
            'глючит', 'баги', 'ошибки', 'не работает', 'сломалось', 'неправильно',
            'некорректно', 'неприятно', 'раздражает', 'бесит', 'злит', 'сложный',
            'неудобный', 'непонятный', 'некачественный', 'старый', 'устаревший',
            'скверно', 'мерзко', 'гадко', 'паршиво', 'неприемлемо', 'расстроен',
            'разочарован', 'зол', 'раздражен', 'беспокоит', 'напрягает', 'утомляет',
            'уныло', 'грустно', 'некомфортно', 'запутался', 'заблудился',
            'неразборчиво', 'мешает', 'путаница', 'хаос', 'беспорядок', 'дешевый',
            'кустарный', 'любительский', 'ненадежный', 'нестабильный', 'глюк',
            'ошибка', 'упал', 'упало', 'завис', 'ошибочно', 'неверно', 'унылый',
            'скучный', 'серый', 'блеклый', 'непривлекательный', 'некрасивый',
            'безвкусный', 'аляповатый', 'зависает', 'тупит', 'долго', 'медленный',
            'разочарование', 'жалоба', 'проблема', 'недостаток', 'минус',
            'не рекомендую', 'не советую', 'бесполезно', 'бессмысленно',
            'ужас', 'кошмарно', 'отстой', ' лажа', 'фигня', 'ерунда', 'беспонтовый',
            'не нравится', 'неуд', 'отвратно', 'мерзость', 'гадость'
        ]
        
        text_fields = [
            self.message,
            self.most_liked,
            self.improvements,
            self.suggestions,
            self.additional_comments
        ]
        
        total_positive = 0
        total_negative = 0
        total_words = 0
        
        for text in text_fields:
            if text and text.strip():
                text_lower = text.lower()
                words = text_lower.split()
                total_words += len(words)
                
                for positive_word in POSITIVE_WORDS:
                    if positive_word in text_lower:
                        count = text_lower.count(positive_word)
                        total_positive += count
                
                for negative_word in NEGATIVE_WORDS:
                    if negative_word in text_lower:
                        count = text_lower.count(negative_word)
                        total_negative += count
        
        base_score = 2.5
        
        if total_words > 0:
            sentiment_adjustment = (total_positive * 0.3) - (total_negative * 0.3)
            adjusted_score = base_score + sentiment_adjustment
            adjusted_score = max(0, min(5, adjusted_score))
            final_score = base_score * 0.3 + adjusted_score * 0.7
            final_score = round(final_score, 2)
        else:
            final_score = base_score
        
        return final_score

    def calculate_comments_sentiment(self):
        return self.analyze_comments_sentiment()

    def calculate_total_score(self):
        total = 0
        
        rating_fields = [
            'site_design_rating',
            'usability_rating',
            'content_rating',
            'speed_rating'
        ]
        for field in rating_fields:
            value = getattr(self, field, 0)
            total += value * 4
        
        sentiment_score = self.calculate_comments_sentiment()
        total += (sentiment_score * 5)
        
        if self.would_recommend:
            recommendation_scores = {
                'definitely': 20,
                'probably': 15,
                'not_sure': 10,
                'probably_not': 5,
                'definitely_not': 0
            }
            total += recommendation_scores.get(self.would_recommend, 0)
        
        if self.overall_satisfaction:
            satisfaction_scores = {
                'very_satisfied': 20,
                'satisfied': 15,
                'neutral': 10,
                'unsatisfied': 5,
                'very_unsatisfied': 0
            }
            total += satisfaction_scores.get(self.overall_satisfaction, 0)
        
        return round(total)

    def calculate_max_possible_score(self):
        return 165

    def calculate_average_rating(self):
        rating_fields = [
            self.site_design_rating,
            self.usability_rating,
            self.content_rating,
            self.speed_rating
        ]
        valid_ratings = [r for r in rating_fields if r > 0]
        
        stars_avg = 0
        if valid_ratings:
            stars_avg = sum(valid_ratings) / len(valid_ratings)
        
        choice_avg = 0
        choice_count = 0
        
        if self.would_recommend:
            choice_scores = {
                'definitely': 5,
                'probably': 4,
                'not_sure': 3,
                'probably_not': 2,
                'definitely_not': 1
            }
            choice_avg += choice_scores.get(self.would_recommend, 0)
            choice_count += 1
        
        if self.overall_satisfaction:
            satisfaction_scores = {
                'very_satisfied': 5,
                'satisfied': 4,
                'neutral': 3,
                'unsatisfied': 2,
                'very_unsatisfied': 1
            }
            choice_avg += satisfaction_scores.get(self.overall_satisfaction, 0)
            choice_count += 1
        
        if choice_count > 0:
            choice_avg = choice_avg / choice_count
        
        sentiment_score = self.calculate_comments_sentiment()
        
        total_avg = 0
        weight_sum = 0
        
        if stars_avg > 0:
            total_avg += stars_avg * 0.35
            weight_sum += 0.35
        
        if choice_avg > 0:
            total_avg += choice_avg * 0.35
            weight_sum += 0.35
        
        if sentiment_score > 0:
            total_avg += sentiment_score * 0.3
            weight_sum += 0.3
        
        if weight_sum == 0:
            return 0
        
        return round(total_avg / weight_sum, 2)

    def get_final_site_rating(self):
        return self.calculate_average_rating()

    def get_rating_display(self):
        rating = self.get_final_site_rating()
        stars = ''
        for i in range(1, 6):
            if i <= rating:
                stars += '★'
            elif i - 1 < rating < i:
                stars += '★'
            else:
                stars += '☆'
        return stars

    def get_score_percentage(self):
        if self.max_possible_score == 0:
            return 0
        return round((self.total_score / self.max_possible_score) * 100, 1)

    def save(self, *args, **kwargs):
        self.comments_sentiment_score = self.calculate_comments_sentiment()
        self.total_score = self.calculate_total_score()
        self.max_possible_score = self.calculate_max_possible_score()
        self.average_rating = self.calculate_average_rating()
        super().save(*args, **kwargs)

    def filename(self):
        if self.attach_file:
            return os.path.basename(self.attach_file.name)
        return "Нет файла"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']


class FeedbackLike(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['feedback', 'user']
        verbose_name = "Лайк отзыва"
        verbose_name_plural = "Лайки отзывов"
    
    def __str__(self):
        return f"Лайк от {self.user.username} на отзыв #{self.feedback.id}"