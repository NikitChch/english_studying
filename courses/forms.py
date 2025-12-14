from django import forms
from .models import CourseOrder, Course, CourseModule

class CourseEnrollForm(forms.Form):
    
    agree_terms = forms.BooleanField(
        required=True,
        label="Я согласен с условиями обучения",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ваши пожелания или вопросы...'
        }),
        label="Комментарии"
    )


class CourseCompleteForm(forms.Form):
    
    confirm_completion = forms.BooleanField(
        required=True,
        label="Подтверждаю, что полностью прошел курс",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    rating = forms.ChoiceField(
        required=True,
        label="Оцените курс",
        choices=[(i, f'{i} звезд') for i in range(1, 6)],
        widget=forms.RadioSelect()
    )
    
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Поделитесь своими впечатлениями о курсе...'
        }),
        label="Ваш отзыв"
    )


class CourseCreateForm(forms.ModelForm):
    
    class Meta:
        model = Course
        fields = [
            'name', 'description', 'level',
            'price', 'start_date', 'end_date', 'max_students'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("Дата окончания должна быть позже даты начала")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.teacher:
            instance.teacher = self.teacher
        if commit:
            instance.save()
        return instance


class CourseEditForm(forms.ModelForm):
    
    class Meta:
        model = Course
        fields = [
            'name', 'description', 'level',
            'price', 'start_date', 'end_date', 'max_students'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("Дата окончания должна быть позже даты начала")
        
        max_students = cleaned_data.get('max_students')
        if max_students and max_students < self.instance.current_students:
            raise forms.ValidationError(
                f"Максимальное количество студентов ({max_students}) "
                f"не может быть меньше текущего ({self.instance.current_students})"
            )
        
        return cleaned_data


class ModuleForm(forms.ModelForm):
    
    class Meta:
        model = CourseModule
        fields = ['title', 'description', 'order', 'duration_hours']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


ModuleFormSet = forms.inlineformset_factory(
    Course,
    CourseModule,
    form=ModuleForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)