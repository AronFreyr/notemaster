from django import forms
from .models import Tag


class AddTagForm(forms.ModelForm):
    tag_name = forms.CharField(label='Input new tag here:')  # The tag to be added.
    current_document = forms.CharField(widget=forms.HiddenInput())  # The document that the tag gets added to.

    class Meta:
        model = Tag
        fields = ['tag_name']
