from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ('name','surname', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user    


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['email'] = self.fields.pop('username')
        self.fields['email'].label = 'Email'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'avatar',
            'name',
            'surname',
            'about',
            'phone',
            'github_url'
        )
        widgets = {
            'about': forms.Textarea(atts={'rows': 4}),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    pass