from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=500, label='Email')
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label='Data urodzenia')
    terms_accepted = forms.BooleanField(required=True, initial=False, label='Akceptuję warunki korzystania ze strony')

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'date_of_birth',
            'terms_accepted'
        )

        labels = {'username': 'Login'}

    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields['password1'].label = 'Hasło'
          self.fields['password2'].label = 'Powtórz hasło'
