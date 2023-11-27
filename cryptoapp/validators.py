# cryptoapp/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import User

def validate_email_value(value):
    user_total = User.objects.filter(email=value)
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            f"This email is already taken.",
            params={'value': value}
        )
def validate_password_uppercase(value):
    if not any(char.isupper() for char in value):
        raise ValidationError(
            _("The password must contain at least one uppercase letter."),
            code='password_no_uppercase',
        )


def validate_password_lowercase(value):
    if not any(char.islower() for char in value):
        raise ValidationError(
            _("The password must contain at least one lowercase letter."),
            code='password_no_lowercase',
        )


def validate_password_special_characters(value):
    special_characters = set('!@#$%^&*()_-+={}[]|\:;"<>,.?/~`')
    if not any(char in special_characters for char in value):
        raise ValidationError(
            _("The password must contain at least one special character."),
            code='password_no_special_characters',
        )


def validate_mobile_number(value):
    if not value.isdigit() or len(value) != 10:
        raise ValidationError(
            _("Mobile number must be a 10-digit number."),
            code='invalid_mobile_number',
        )
