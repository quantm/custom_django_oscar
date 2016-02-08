#__author__ = 'tqn'
from django import forms
from django.core import validators
from django.utils.translation import ugettext as _

PRODUCT_OPTIONS = (
    ('1', _('To a List')),
    ('0', _('To My Images')),
)
VIDEO_OPTIONS = (
    ('1', _('To My Video')),
    ('0', _('To My Images')),
)


class BookmarkLetForm(forms.Form):
    title = forms.CharField(error_messages={'required': _('Please enter title')})
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'cols': '15', 'onclick': 'hashtag(this.id)'}), label=_('Description'), required=False)
    image = forms.CharField(widget=forms.HiddenInput)
    is_product = forms.ChoiceField(choices=PRODUCT_OPTIONS)
    video_code = forms.CharField(widget=forms.HiddenInput)
    is_video = forms.ChoiceField(choices=VIDEO_OPTIONS)


class BookmarkLetSignInForm(forms.Form):
    username = forms.CharField(
        label=_('Your name'),
        validators=[validators.EMPTY_VALUES],
        error_messages={'required': _('Your name is required')}
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput,
        validators=[validators.EMPTY_VALUES],
        error_messages={'required': _('Password is required')}
    )