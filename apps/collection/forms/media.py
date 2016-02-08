#__author__ = 'tqn'
from django import forms
from django.utils.translation import ugettext as _

class CollectionVideo_Form(forms.Form):
    title = forms.CharField(error_messages={'required': _('Please enter title')})
    video_code = forms.CharField(widget=forms.HiddenInput)
    image = forms.CharField(widget=forms.HiddenInput)
    description = forms.CharField(widget=forms.Textarea, label=_('Description'), required=False)

class CollectionImage_Form(forms.Form):
    title = forms.CharField(error_messages={'required': _('Please enter title')})
    image = forms.CharField(widget=forms.HiddenInput)
    description = forms.CharField(widget=forms.Textarea, label=_('Description'), required=False)



