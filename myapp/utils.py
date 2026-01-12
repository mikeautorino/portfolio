from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def is_valid_email_format(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
