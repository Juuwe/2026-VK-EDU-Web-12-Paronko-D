from django import forms
from django.core.exceptions import ValidationError
from .models import Profile

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.password_validation import password_validators_help_texts
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

FIELD_CLASS = 'form-control border-2 shadow-sm'
MAX_AVATAR_SIZE = 2 * 1024 * 1024

class UserModelBaseForm(forms.ModelForm):
    username = forms.CharField(max_length=32, label='Логин', widget=forms.TextInput(attrs={'class': FIELD_CLASS,'placeholder': 'Придумайте логин (a-z, A-Z, 0-9, макс. 32 симв.)'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': FIELD_CLASS, 'placeholder': 'example@email.com'}))
    nickname = forms.CharField(label='Никнейм', widget=forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': 'Придумайте никнейм'}))
    avatar = forms.ImageField(required=False, label='Фото профиля', widget=forms.FileInput(attrs={'class': 'form-control border-2 shadow-sm','accept': 'image/jpeg,image/png'}), help_text='Выберите изображение (JPG, PNG; до 2 МБ)')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if not avatar:
            return avatar

        if avatar.size > MAX_AVATAR_SIZE:
            raise ValidationError('Размер файла не должен превышать 2 МБ')

        return avatar

class SignupForm(UserModelBaseForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': FIELD_CLASS, 'placeholder': 'Введите Ваш пароль'}),
        validators=[validate_password],
        help_text=password_validators_help_texts(),
        error_messages={'required': 'Пароль не может быть пустым'}
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': FIELD_CLASS, 'placeholder': 'Подтвердите пароль'})
    )

    class Meta(UserModelBaseForm.Meta):
        fields = UserModelBaseForm.Meta.fields + ['password']

    def clean_nickname(self):
        nickname_clean = self.cleaned_data.get('nickname')
        if Profile.objects.filter(nickname=nickname_clean).exists():
            raise ValidationError("Этот никнейм уже занят")
        return nickname_clean

    def clean(self):
        cleaned_data = super().clean()
        password_clean = cleaned_data.get('password')
        password_conf_clean = cleaned_data.get('password_confirm')

        if password_clean and password_conf_clean and password_clean != password_conf_clean :
            self.add_error('password_confirm', 'Пароли не совпадают')

        return cleaned_data

    def save(self):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()

        Profile.objects.create(user=user, nickname=self.cleaned_data['nickname'], avatar=self.cleaned_data['avatar'])

        return user

    field_order = ['username', 'email', 'nickname', 'password', 'password_confirm', 'avatar']

class SettingsForm(UserModelBaseForm):
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_nickname(self):
        nickname_clean = self.cleaned_data.get('nickname')
        if not nickname_clean:
            raise ValidationError('Заполните никнейм')
        if Profile.objects.filter(nickname=nickname_clean).exclude(user=self.user_instance).exists():
            raise ValidationError('Этот никнейм уже занят')
        return nickname_clean

    def save(self):
        user = super().save()
        profile = user.profile
        profile.nickname = self.cleaned_data.get('nickname')

        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data.get('avatar')

        profile.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': 'your_login'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': FIELD_CLASS, 'placeholder': 'your_password123'})
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Запомнить меня',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.authenticated_user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        username_clean = self.cleaned_data.get('username')
        password_clean = self.cleaned_data.get('password')

        if username_clean and password_clean:
            self.authenticated_user = authenticate(username=username_clean, password=password_clean)

            if self.authenticated_user is None:
                raise ValidationError('Неверный логин или пароль')

        return cleaned_data

    def get_user(self):
        return self.authenticated_user
