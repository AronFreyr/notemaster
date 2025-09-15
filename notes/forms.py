from django import forms
from django.db import models
from .models import Tag, Image, Document
from tinymce.widgets import TinyMCE


class CreateItemForm(forms.Form):
    """
    Abstract base class for forms that create items like documents or images.
    """

    def get_name_field(self):
        raise NotImplementedError("Subclasses must implement get_name_field method")

    def get_name_label(self):
        raise NotImplementedError("Subclasses must implement get_name_label method")

    def get_text_field(self):
        raise NotImplementedError("Subclasses must implement get_text_field method")

    def get_text_label(self):
        raise NotImplementedError("Subclasses must implement get_text_label method")

    def get_tag_field(self):
        raise NotImplementedError("Subclasses must implement get_tag_field method")

    def get_tag_label(self):
        raise NotImplementedError("Subclasses must implement get_tag_label method")

class AddTagForm(forms.ModelForm):
    # The tag to be added.
    tag_name = forms.CharField(label='Input new tag here:', required=False)
    # The document that the tag gets added to.
    current_document = forms.CharField(widget=forms.HiddenInput(), required=False)
    # The Image that the tag gets added to.
    current_image = forms.CharField(widget=forms.HiddenInput(), required=False)

    def cleaned_tag(self):
        return self.cleaned_data['tag_name']

    def cleaned_document(self):
        return self.cleaned_data['current_document']

    def cleaned_image(self):
        return self.cleaned_data['current_image']

    class Meta:
        model = Tag
        fields = ['tag_name']


class CreateDocumentFormOld(forms.Form):
    document_name = forms.CharField(label='Document name:', required=True)
    # document_text = forms.CharField(label='Document text:', widget=forms.Textarea)
    document_text = forms.CharField(label='Document text:',
                                    widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    new_tag = forms.CharField(label='Document tags:')

    # formfield_overrides = {models.TextField: {'widget': TinyMCE()}}

    class Meta:
        fields = ['document_name', 'document_text', 'new_tag']


class CreateDocumentForm(forms.Form):
    document_name = forms.CharField(label='Document name:', required=True)
    document_text = forms.CharField(label='Document text:',
                                    widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    new_tag = forms.CharField(label='Document tags:')


    def get_name_field(self):
        if not self.is_valid():
            return self['document_name']
        return self.cleaned_data['document_name']

    def get_name_label(self):
        if not self.is_valid():
            return self['document_name'].label
        return self.fields['document_name'].label

    def get_text_field(self):
        if not self.is_valid():
            return self['document_text']
        return self.cleaned_data['document_text']

    def get_text_label(self):
        if not self.is_valid():
            return self['document_text'].label
        return self.fields['document_text'].label

    def get_tag_field(self):
        if not self.is_valid():
            return self['new_tag']
        return self.cleaned_data['new_tag']

    def get_tag_label(self):
        if not self.is_valid():
            return self['new_tag'].label
        return self.fields['new_tag'].label

    class Meta:
        fields = ['document_name', 'document_text', 'new_tag']


class CreateImageFormOld(forms.Form):
    image_name = forms.CharField(label='Image name:')
    image_text = forms.CharField(label='Image text:', required=False,
                                 widget=forms.Textarea)
    image_picture = forms.FileField(label='Image picture:')
    new_tag = forms.CharField(label='Image tags:')

    class Meta:
        model = Image
        fields = ['image_name', 'image_text', 'image_picture', 'new_tag']


class CreateImageForm(CreateItemForm):
    image_name = forms.CharField(label='Image name:')
    image_text = forms.CharField(label='Image text:', required=False,
                                 widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    image_picture = forms.FileField(label='Image picture:')
    new_tag = forms.CharField(label='Image tags:')

    def get_name_field(self):
        if not self.is_valid():
            return self['image_name']
        return self.cleaned_data['image_name']

    def get_name_label(self):
        if not self.is_valid():
            return self['image_name'].label
        return self.fields['image_name'].label

    def get_text_field(self):
        if not self.is_valid():
            return self['image_text']
        return self.cleaned_data['image_text']

    def get_text_label(self):
        if not self.is_valid():
            return self['image_text'].label
        return self.fields['image_text'].label

    def get_tag_field(self):
        if not self.is_valid():
            return self['new_tag']
        return self.cleaned_data['new_tag']

    def get_tag_label(self):
        if not self.is_valid():
            return self['new_tag'].label
        return self.fields['new_tag'].label

    class Meta:
        model = Image
        fields = ['image_name', 'image_text', 'image_picture', 'new_tag']


class EditDocumentForm(forms.ModelForm):
    document_text = forms.CharField(label=False, widget=TinyMCE())

    class Meta:
        model = Document
        fields = ['document_text']
