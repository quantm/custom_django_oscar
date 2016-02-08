#__author__ = 'tqn'
from django import forms
from oscar.apps.catalogue.models import ProductClass

class ProductForm(forms.Form):
    title = forms.CharField(error_messages={'required': 'Please enter title'})
    description = forms.CharField(widget=forms.Textarea, label='Description', required=False)
    image = forms.CharField(widget=forms.HiddenInput)