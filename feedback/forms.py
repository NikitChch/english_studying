from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    average_rating = forms.FloatField(widget=forms.HiddenInput(), required=False)
    total_score = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    max_possible_score = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    comments_sentiment_score = forms.FloatField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Feedback
        fields = [
            'feedback_type',
            'subject', 'message',
            'site_design_rating', 'usability_rating', 'content_rating', 'speed_rating',
            'would_recommend', 'overall_satisfaction',
            'most_liked', 'improvements', 'suggestions', 'additional_comments',
            'average_rating', 'total_score', 'max_possible_score', 'comments_sentiment_score',
            'subscribe_newsletter', 'attach_file',
        ]
        
        widgets = {
            'feedback_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите тему отзыва',
                'required': 'required'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Опишите ваши впечатления от сайта...',
                'required': 'required'
            }),
            
            'site_design_rating': forms.HiddenInput(attrs={'value': '0'}),
            'usability_rating': forms.HiddenInput(attrs={'value': '0'}),
            'content_rating': forms.HiddenInput(attrs={'value': '0'}),
            'speed_rating': forms.HiddenInput(attrs={'value': '0'}),
            
            'would_recommend': forms.Select(attrs={
                'class': 'form-select choice-select'
            }),
            'overall_satisfaction': forms.Select(attrs={
                'class': 'form-select choice-select'
            }),
            
            'most_liked': forms.Textarea(attrs={
                'class': 'form-control open-question',
                'rows': 3,
                'placeholder': 'Что вам больше всего понравилось на сайте?...'
            }),
            'improvements': forms.Textarea(attrs={
                'class': 'form-control open-question',
                'rows': 3,
                'placeholder': 'Что можно улучшить в работе сайта?...'
            }),
            'suggestions': forms.Textarea(attrs={
                'class': 'form-control open-question',
                'rows': 3,
                'placeholder': 'Какие новые функции были бы полезны?...'
            }),
            'additional_comments': forms.Textarea(attrs={
                'class': 'form-control open-question',
                'rows': 3,
                'placeholder': 'Любые дополнительные мысли и пожелания...'
            }),
            
            'subscribe_newsletter': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'attach_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.pdf,.doc,.docx'
            }),
            
            'average_rating': forms.HiddenInput(),
            'total_score': forms.HiddenInput(),
            'max_possible_score': forms.HiddenInput(),
            'comments_sentiment_score': forms.HiddenInput(),
        }
        
        labels = {
            'feedback_type': 'Тип отзыва *',
            'subject': 'Тема отзыва *',
            'message': 'Текст отзыва *',
            'site_design_rating': '',
            'usability_rating': '',
            'content_rating': '',
            'speed_rating': '',
            'would_recommend': 'Порекомендуете ли вы наш сайт друзьям?',
            'overall_satisfaction': 'Общая удовлетворенность сервисом',
            'most_liked': 'Что больше всего понравилось?',
            'improvements': 'Что можно улучшить?',
            'suggestions': 'Ваши предложения',
            'additional_comments': 'Дополнительные комментарии',
            'subscribe_newsletter': 'Хочу получать новости и обновления',
            'attach_file': 'Прикрепить файл',
            'average_rating': '',
            'total_score': '',
            'max_possible_score': '',
            'comments_sentiment_score': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['site_design_rating'].initial = 0
        self.fields['usability_rating'].initial = 0
        self.fields['content_rating'].initial = 0
        self.fields['speed_rating'].initial = 0
        
        self.fields['average_rating'].initial = 0
        self.fields['total_score'].initial = 0
        self.fields['max_possible_score'].initial = 165
        self.fields['comments_sentiment_score'].initial = 2.5
        
        self.fields['feedback_type'].required = True
        self.fields['subject'].required = True
        self.fields['message'].required = True
        
        self.fields['would_recommend'].required = False
        self.fields['overall_satisfaction'].required = False
        
        self.fields['most_liked'].required = False
        self.fields['improvements'].required = False
        self.fields['suggestions'].required = False
        self.fields['additional_comments'].required = False
        
        if 'is_processed' in self.fields:
            self.fields['is_processed'].widget = forms.HiddenInput()
            self.fields['is_processed'].initial = False

    def clean_attach_file(self):
        file = self.cleaned_data.get('attach_file')
        if file:
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Размер файла не должен превышать 5MB")
            
            allowed_types = [
                'image/jpeg', 
                'image/png', 
                'application/pdf', 
                'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Разрешены только файлы: JPG, PNG, PDF, DOC, DOCX")
        
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not cleaned_data.get('comments_sentiment_score'):
            cleaned_data['comments_sentiment_score'] = 2.5
            
        if not cleaned_data.get('average_rating'):
            cleaned_data['average_rating'] = 0
            
        if not cleaned_data.get('total_score'):
            cleaned_data['total_score'] = 0
            
        if not cleaned_data.get('max_possible_score'):
            cleaned_data['max_possible_score'] = 165
        
        return cleaned_data