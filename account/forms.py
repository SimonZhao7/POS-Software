from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    def clean(self):
        cleaned_data = self.cleaned_data
        if CustomUser.objects.all().count() + 1 > 2:
            raise ValidationError('You can only create one user')
        return cleaned_data
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']     
        
    def save(self,  spreadsheet_id, commit=True):
        user = super().save(commit)
        user.spreadsheet_id = spreadsheet_id
        user.save()
        return user