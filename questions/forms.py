from django import forms
from .models import Question, Answer, Tag
from django.core.exceptions import ValidationError

FIELD_CLASS = 'form-control border-2 shadow-sm'

class AskForm(forms.ModelForm):
    tags = forms.CharField(
        label="Теги",
        required=False,
        widget=forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': 'Введите теги через запятую (макс. 5)'}),
        help_text="Разделяйте теги запятыми, макс. 5"
    )

    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': 'Введите тему'}),
            'content': forms.Textarea(attrs={'class': FIELD_CLASS, 'rows': 5, 'placeholder': 'Опишите проблему'}),
        }

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if not tags_str:
            return []

        tag_list = list([t.strip() for t in tags_str.split(',') if t.strip()])
        if len(tag_list) > 5:
            raise ValidationError('Тегов должно быть не больше 5')

        for tag_name in tag_list:
            if len(tag_name) > 25:
                raise ValidationError(f'Тег "{tag_name}" слишком длинный. Макс. длина - 25 симв.')

        return tag_list

    def save(self, commit=True):
        question = super().save(commit=False)

        question.author = self._user.profile

        if commit:
            question.save()

            tag_list = self.cleaned_data.get('tags')
            for tag_name in tag_list:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)

        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Напишите решение здесь...'}),
        }

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        self._question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self._user.profile
        answer.question = self._question
        if commit:
            answer.save()
        return answer
