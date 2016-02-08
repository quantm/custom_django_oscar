#__author__ = 'tqn'
from django import forms

class CollectionForm(forms.Form):
    name = forms.CharField(max_length=255, required=False)


class MyListForm(forms.Form):
    name = forms.CharField(max_length=255, required=False)