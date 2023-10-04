from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver']
        labels = {'receiver': 'Odbiorca'}

    def clean(self):
        # data is feteched using the super function of django
        super(MessageForm, self).clean()

        receiver = self.cleaned_data.get('receiver')
        sender = self.cleaned_data.get('sender')
        # Nazwa grupy
        if receiver is None:
            self._errors['receiver'] = self.error_class([
                'Nie ma takiego użytkownika.'
            ])

        if receiver == sender:
            self._errors['receiver'] = self.error_class([
                'Nie możesz wysłać zaproszenia do samego siebie!'
            ])

        return self.cleaned_data
