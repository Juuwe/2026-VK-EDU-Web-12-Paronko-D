from django import forms
from django.core.exceptions import ValidationError
import re

FIELD_CLASS = 'form-control border-2 shadow-sm'
MAX_AVATAR_SIZE = 2 * 1024 * 1024

class LoginFieldMixin(forms.Form):
    login = forms.CharField(
        min_length=3,
        max_length=32,
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': FIELD_CLASS,
            'placeholder': 'Придумайте логин (a-z, A-Z, 0-9, 3-32 симв.)'
        })
    )

    def clean_login(self):
        login = self.cleaned_data.get('login')
        login_regex = r'^[a-zA-Z0-9]{3,32}$'

        if not re.match(login_regex, login):
            raise ValidationError('Логин не соответствует формату')

        return login

class EmailFieldMixin(forms.Form):
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': FIELD_CLASS,
            'placeholder': 'example@email.com'
        }),

        error_messages={
            'required': 'Обязательное поле',
            'invalid': 'Введите email в указанном формате'
        }
    )

class PasswordFieldMixin(forms.Form):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': FIELD_CLASS, 'placeholder': 'Введите Ваш пароль'})
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        errors = []

        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError('Только латинский алфавит A-Z, a-z')

        if not re.search(r'[0-9]', password):
            errors.append('Цифры 0-9')

        if not re.search(r'[A-Z]', password):
            errors.append('Хотя бы одна заглавная')

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append('Хотя бы один спец. символ')

        if errors:
            raise ValidationError(errors)

        return password

class AvatarFieldMixin(forms.Form):
    avatar = forms.ImageField(
        required=False,
        label='Фото профиля',
        widget=forms.FileInput(attrs={
            'class': 'form-control border-2 shadow-sm',
            'accept': 'image/jpeg,image/png'
        }),
        help_text='Выберите изображение (JPG, PNG; до 2 МБ)',
        error_messages={
            'invalid': 'Загрузите корректное изображение',
        }
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if not avatar:
            return avatar

        if avatar.size > MAX_AVATAR_SIZE:
            raise ValidationError('Размер файла не должен превышать 2 МБ')

        return avatar

class NicknameFieldMixin(forms.Form):
    nickname = forms.CharField(
        label='Никнейм',
        required=True,
        widget=forms.TextInput(attrs={
            'class': FIELD_CLASS,
            'placeholder': 'Придумайте никнейм'
        }),

        error_messages={
            'required': 'Обязательное поле',
        }
    )

    def clean_nickname(self):
        pass

class LoginForm(PasswordFieldMixin, forms.Form):
    login_or_email = forms.CharField(
        min_length=3,
        max_length=32,
        label='Логин или Email',
        widget=forms.TextInput(attrs={
            'class': FIELD_CLASS,
            'placeholder': 'Введите Ваш логин или email'
        })
    )

    remember_me = forms.BooleanField(
        required=False,
        label='Запомнить меня',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    field_order = ['login_or_email', 'password']

    def clean_password(self):
        return self.cleaned_data.get('password')


class SignupForm(LoginFieldMixin, EmailFieldMixin, NicknameFieldMixin, PasswordFieldMixin, AvatarFieldMixin, forms.Form):
    password_confirm = forms.CharField(
        min_length=8,
        required=True,
        label='Подтвердите пароль',
        widget=forms.PasswordInput(attrs={
            'class': FIELD_CLASS,
            'placeholder': 'Повторите пароль',
        })
    )

    field_order = ['login', 'email', 'nickname', 'password', 'password_confirm', 'avatar']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Пароли не совпадают')

        return cleaned_data


class SettingsForm(LoginFieldMixin, NicknameFieldMixin, EmailFieldMixin, AvatarFieldMixin, forms.Form):
    field_order = ['login', 'email', 'nickname', 'avatar']
