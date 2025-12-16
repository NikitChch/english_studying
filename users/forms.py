from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=(('student', 'Студент'), ('teacher', 'Преподаватель')),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    group = forms.CharField(
        required=False,
        widget=forms.Select(choices=[
            ('', 'Выберите группу'),
            ('A1', 'A1'),
            ('A2', 'A2'),
            ('B1', 'B1'),
            ('B2', 'B2'),
            ('C1', 'C1'),
        ], attrs={'class': 'form-control'}),
        label="Уровень английского"
    )
    
    level = forms.CharField(
        required=False,
        widget=forms.Select(choices=[
            ('', 'Выберите уровень'),
            ('Начальный', 'Начальный'),
            ('Элементарный', 'Элементарный'),
            ('Средний', 'Средний'),
            ('Выше среднего', 'Выше среднего'),
            ('Продвинутый', 'Продвинутый'),
        ], attrs={'class': 'form-control'})
    )
    
    specialization = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: Бизнес-английский, Подготовка к IELTS'
        })
    )
    
    experience = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '50',
            'placeholder': '0'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'user_type', 'group', 'level', 'specialization', 'experience',
            'first_name', 'last_name', 'phone'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефон'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'student':
            if not cleaned_data.get('group'):
                self.add_error('group', 'Для студента необходимо указать группу')
            if not cleaned_data.get('level'):
                self.add_error('level', 'Для студента необходимо указать уровень')
        
        elif user_type == 'teacher':
            if not cleaned_data.get('specialization'):
                self.add_error('specialization', 'Для преподавателя необходимо указать специализацию')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data['user_type']
        user.group = self.cleaned_data.get('group', '')
        user.level = self.cleaned_data.get('level', '')
        user.specialization = self.cleaned_data.get('specialization', '')
        
        experience = self.cleaned_data.get('experience')
        if experience is None:
            user.experience = 0
        else:
            user.experience = experience
        
        if commit:
            user.save()
        
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя или Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя или email'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    specialization = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: Бизнес-английский, Подготовка к IELTS'
        })
    )
    
    experience = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '50',
            'placeholder': '0'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone', 
            'profile_picture', 'specialization', 'experience'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user_type == 'student':
            self.fields.pop('specialization')
            self.fields.pop('experience')


class PasswordResetCodeForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.HiddenInput()
    )
    
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        label='Код подтверждения',
        widget=forms.HiddenInput()
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise forms.ValidationError('Код должен содержать только цифры')
        return code