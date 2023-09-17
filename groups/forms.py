from django import forms
from .models import CommonGroups


class CommonGroupsForm(forms.ModelForm):
    class Meta:
        model = CommonGroups
        fields = ['group_name', 'max_number_of_members','password']
