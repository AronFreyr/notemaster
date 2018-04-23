from django import forms
from .models import Tag


class AddTagForm(forms.ModelForm):
    tag_name = forms.CharField(label='Input new tag here:')  # The tag to be added.
    current_document = forms.CharField(widget=forms.HiddenInput())  # The document that the tag gets added to.

    def cleaned_tag(self):
        return self.cleaned_data['tag_name']

    def cleaned_document(self):
        return self.cleaned_data['current_document']

    class Meta:
        model = Tag
        fields = ['tag_name']


class CreateDocumentForm(forms.Form):
    document_name = forms.CharField(label='Document name:')
    document_text = forms.CharField(label='Document text:')
    new_tag = forms.CharField(label='Input new tag here:')

    class Meta:
        fields = ['document_name', 'document_text', 'new_tag']
