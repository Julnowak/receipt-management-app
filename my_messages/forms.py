from django import forms
from .models import Message
from django.forms import HiddenInput


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver']
        labels = {'receiver': 'Odbiorca'}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        self.members = kwargs.pop('members',None)
        super().__init__(*args, **kwargs)

    def clean(self):
        # data is feteched using the super function of django
        super(MessageForm, self).clean()

        receiver = self.cleaned_data.get('receiver')
        sender = self.user

        # Nazwa grupy
        if receiver is None:
            self._errors['receiver'] = self.error_class([
                'Nie ma takiego użytkownika.'
            ])

        if receiver == sender:
            self._errors['receiver'] = self.error_class([
                'Nie możesz wysłać zaproszenia do samego siebie!'
            ])

        if receiver in self.members.all():
            self._errors['receiver'] = self.error_class([
                'Ta osoba należy już do grupy.'
            ])

        return self.cleaned_data


class NewMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver','text','title']
        labels = {'receiver': 'Odbiorca', 'text': "Treść wiadomości", 'title': "Tytuł"}

        widgets = {
            'receiver': forms.TextInput(
                attrs={'class': "form-control",}
            ),

            'title': forms.TextInput(
                attrs={'class': "form-control", }
            ),

            'text': forms.Textarea(
                attrs={'class': "form-control", }
            ),
        }

    def clean(self):
        # data is feteched using the super function of django
        super(NewMessageForm, self).clean()
        receiver = self.cleaned_data.get('receiver')
        # Nazwa grupy
        if receiver is None:
            self._errors['receiver'] = self.error_class([
                'Nie ma takiego użytkownika.'
            ])


class HiddenMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver']
        labels = {'receiver': 'Odbiorca'}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        self.members = kwargs.pop('members',None)
        super().__init__(*args, **kwargs)

    def clean(self):
        # data is feteched using the super function of django
        super(HiddenMessageForm, self).clean()

        receiver = self.cleaned_data.get('receiver')
        sender = self.user

        # Nazwa grupy
        if receiver is None:
            self._errors['receiver'] = self.error_class([
                'Nie ma takiego użytkownika.'
            ])

        return self.cleaned_data