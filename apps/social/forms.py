from django import forms


class MyEventCreateViewForm(forms.Form):
    name = forms.CharField(error_messages={'required': 'Please enter title'})
    date_created = forms.DateTimeField(error_messages={'required': 'Please selecte date for your event'})
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'cols': '15'}),
                                  label='Description', required=False)
