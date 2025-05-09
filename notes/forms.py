from django import forms
from django.db import models
from .models import Tag, Image, Document
from tinymce.widgets import TinyMCE


class AddTagForm(forms.ModelForm):
    tag_name = forms.CharField(label='Input new tag here:', required=False)  # The tag to be added.
    current_document = forms.CharField(widget=forms.HiddenInput(),
                                       required=False)  # The document that the tag gets added to.
    current_image = forms.CharField(widget=forms.HiddenInput(),
                                    required=False)  # The Image that the tag gets added to.

    def cleaned_tag(self):
        return self.cleaned_data['tag_name']

    def cleaned_document(self):
        return self.cleaned_data['current_document']

    def cleaned_image(self):
        return self.cleaned_data['current_image']

    class Meta:
        model = Tag
        fields = ['tag_name']


class CreateDocumentForm(forms.Form):
    document_name = forms.CharField(label='Document name:')
    # document_text = forms.CharField(label='Document text:', widget=forms.Textarea)
    document_text = forms.CharField(label='Document text:', widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    new_tag = forms.CharField(label='Document tags:')

    # formfield_overrides = {models.TextField: {'widget': TinyMCE()}}

    class Meta:
        fields = ['document_name', 'document_text', 'new_tag']


class CreateImageForm(forms.Form):
    image_name = forms.CharField(label='Image name:')
    image_text = forms.CharField(label='Image text:', required=False, widget=forms.Textarea)
    image_picture = forms.FileField(label='Image picture:')
    new_tag = forms.CharField(label='Image tags:')

    class Meta:
        model = Image
        fields = ['image_name', 'image_text', 'image_picture', 'new_tag']


class EditDocumentForm(forms.ModelForm):
    document_text = forms.CharField(label=False, widget=TinyMCE())

    class Meta:
        model = Document
        fields = ['document_text']
