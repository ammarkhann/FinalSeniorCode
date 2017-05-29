from django import forms
from .models import FreeTextAnswer

class UserResponseForm(forms.Form):
	question_id = forms.IntegerField()
	answer_id = forms.IntegerField()
	


class UserTextFreeForm(forms.Form):
	question_id = forms.IntegerField()
	my_answer = forms.CharField(widget=forms.Textarea)


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )
