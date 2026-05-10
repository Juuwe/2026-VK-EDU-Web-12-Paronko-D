from django.core.exceptions import ValidationError

def validate_created_date(create_at_before, created_at_after, message):
    if created_at_after and created_at_after and create_at_before > created_at_after:
        raise ValidationError(message)
