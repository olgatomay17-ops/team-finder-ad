from django import forms
from django.contrib.auth import authenticate
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

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': 'Email'},
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


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
            'about': forms.Textarea(attrs={'rows': 4}),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    pass
