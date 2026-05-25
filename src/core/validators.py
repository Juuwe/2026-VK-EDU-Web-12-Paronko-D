from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_avatar_size = 2 * 1024 * 1024
    if file.size > max_avatar_size:
        raise ValidationError('Файл слишком большой. Максимальный размер 2 МБ')
