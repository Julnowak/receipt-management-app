from django import forms
from .models import Message, User


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
        fields = ['receiver', 'text', 'title']
        labels = {'receiver': 'Odbiorca', 'text': "Treść wiadomości", 'title': "Tytuł"}

        widgets = {
            'receiver': forms.TextInput(
                attrs={'class': "form-control",
                       'style': "border-color: black;"}
            ),

            'title': forms.TextInput(
                attrs={'class': "form-control",
                       'style': "border-color: black;"}
            ),

            'text': forms.Textarea(
                attrs={'class': "form-control",
                       'rows': 14,
                       'style': "border-color: black;"}
            ),
        }

    def clean(self):
        super(NewMessageForm, self).clean()
        receiver = self.cleaned_data.get('receiver')
        print(receiver)
        title = self.cleaned_data.get('title')
        text = self.cleaned_data.get('text')

        if not User.objects.filter(username=receiver):
            self._errors['receiver'] = self.error_class([
                'Nie ma takiego użytkownika.'
            ])
            self.data['receiver'] = ''

        if len(text) < 1:
            self._errors['text'] = self.error_class([
                'Nie można wysłać pustej wiadomości.'
            ])

        if len(title) < 1:
            self._errors['title'] = self.error_class([
                'Proszę dodać wtytuł wiadomości.'
            ])
        elif len(title) > 200:
            self._errors['title'] = self.error_class([
                f'Tytuł nie może przekraczać 200 znaków. Aktualna liczba znaków to {len(title)}.'
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
        super(HiddenMessageForm, self).clean()

        receiver = self.cleaned_data.get('receiver')
        sender = self.user

        # Nazwa grupy
        if receiver is None:
            self._errors['receiver'] = self.error_class([
                'Nie ma takiego użytkownika.'
            ])

        return self.cleaned_data