import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=500, label='Email',
                             widget=forms.EmailInput(attrs={'class': "form-control",
                                                            'style': 'max-width: 300px; margin: auto;border-color: black',
                                                            'placeholder': 'Email'}),
                             error_messages={'invalid': 'Wprowadź poprawny email.'}
                             )
    date_of_birth = forms.DateField(initial=datetime.date(2010, 1, 1),
                                    widget=forms.DateInput(attrs={'type': 'date','class': "form-control",
                                                                  'style': 'max-width: 300px; margin: auto;border-color: black',}), required=True, label='Data urodzenia')
    terms_accepted = forms.BooleanField(required=True,widget=forms.CheckboxInput(attrs={
                'class': "form-check",
                'style': 'width: 25px; height: 25px; border-color: black; accent-color: black',
            }), initial=False, label='Przeczytałem regulamin i akceptuję warunki korzystania z aplikacji.')
    password1 = forms.CharField(widget=forms.PasswordInput(
                    attrs={'class': 'form-control',
                           'style': 'max-width: 300px; margin: auto;border-color: black',
                           'type': 'password', 'name': 'password', 'placeholder': 'Hasło',}),
                    label='')
    password2 = forms.CharField(widget=forms.PasswordInput(
                    attrs={'class': 'form-control',
                           'style': 'max-width: 300px; margin: auto;border-color: black',
                           'type': 'password', 'name': 'password', 'placeholder': 'Powtórz hasło'}),
                    label='')

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
        widgets = {
            'username': forms.TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Login',
                'style': 'max-width: 300px; margin: auto;border-color: black',
            }),
        }

    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields['password1'].label = 'Hasło'
          self.fields['password2'].label = 'Powtórz hasło'

    def clean(self):
        # data is feteched using the super function of django
        super(RegistrationForm, self).clean()

        dob = self.cleaned_data.get('date_of_birth')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Nazwa grupy
        if int(datetime.datetime.today().year - dob.year) < 13:
            self._errors['date_of_birth'] = self.error_class([
                'Musisz mieć minimum 13 lat, aby się zarejestrować.'
            ])
        if password1 != password2:
            self._errors['password2'] = self.error_class([
                'Hasła nie są takie same.'
            ])

