from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    def clean(self):
        cleaned_data = self.cleaned_data
        if User.objects.all().count() + 1 > 2:
            raise ValidationError('You can only create one user')
        return cleaned_data