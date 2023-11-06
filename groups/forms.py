from django import forms
from .models import CommonGroups
from django.contrib.auth.models import User
from django.core import validators


class CommonGroupsForm(forms.ModelForm):
    class Meta:
        model = CommonGroups
        fields = ['group_name', 'max_number_of_members','password']
        labels = {'group_name': 'Nazwa grupy',
                  'max_number_of_members': 'Max. liczba członków',
                  'password': 'Hasło',
                 }

        widgets = {
            'group_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'width: 300px; margin: auto',
                'placeholder': 'Grupa',
                'label': "Hasło"
            }),
            'max_number_of_members': forms.NumberInput(attrs={
                'class': "form-control",
                'style': 'width: 300px; margin: auto',
                'max': '50',
                'min': '1',
                'label': "Hasło"
            }),

            'password': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'width: 300px; margin: auto',
                'label': "Hasło"
            })
        }

    def clean(self):
        # data is feteched using the super function of django
        super(CommonGroupsForm, self).clean()

        group_name = self.cleaned_data.get('group_name')
        max_number_of_members = self.cleaned_data.get('max_number_of_members')
        password = self.cleaned_data.get('password')

        # Nazwa grupy
        if group_name is None:
            self._errors['group_name'] = self.error_class([
                'Nie wpisano nazwy grupy.'
            ])
        elif len(group_name) < 3:
            self._errors['group_name'] = self.error_class([
                'Nazwa musi mieć więcej niż 3 znaki.'
            ])

        # Max liczba członków
        if not isinstance(max_number_of_members,int):
            self._errors['max_number_of_members'] = self.error_class([
                'Należy wprowadzić liczbę od 1 do 50.'
            ])
        else:
            if max_number_of_members < 1:
                self._errors['max_number_of_members'] = self.error_class([
                    'Liczba członków musi być większa od 0.'
                ])
            elif max_number_of_members > 50:
                self._errors['max_number_of_members'] = self.error_class([
                    'Liczba członków musi być mniejsza od 50.'
                ])

        # password
        if password is None:
            self._errors['group_name'] = self.error_class([
                'Nie wpisano hasła.'
            ])
        elif len(password) < 3:
            self._errors['group_name'] = self.error_class([
                'Hasło musi mieć więcej niż 3 znaki.'
            ])

        return self.cleaned_data

