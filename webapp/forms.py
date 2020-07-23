from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

from webapp.models import Project, Invite


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['state']

class RegisterForm(UserCreationForm):
    invite = forms.CharField(max_length=30, label="Инвайт")

    def clean_invite(self):
        invite = self.cleaned_data.get("invite")
        if Invite.objects.filter(code=invite).count() > 0:
            Invite.objects.filter(code=invite).all().delete()
            return invite
        else:
            raise forms.ValidationError(
                "Некорректный инвайт",
                code='invalid_invite',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
