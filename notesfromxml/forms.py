from django import forms
from .models import Tag, Image


class AddTagForm(forms.ModelForm):
    tag_name = forms.CharField(label='Input new tag here:')  # The tag to be added.
    current_document = forms.CharField(widget=forms.HiddenInput(),
                                       required=False)  # The document that the tag gets added to.
    current_image = forms.CharField(widget=forms.HiddenInput(),
                                    required=False)  # The document that the tag gets added to.

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
    document_text = forms.CharField(label='Document text:')
    new_tag = forms.CharField(label='Input new tag here:')

    class Meta:
        fields = ['document_name', 'document_text', 'new_tag']


class CreateImageForm(forms.Form):
    image_name = forms.CharField(label='Image name:')
    image_text = forms.CharField(label='Image text:', required=False, widget=forms.Textarea)
    image_picture = forms.FileField(label='Image picture:')
    new_tag = forms.CharField(label='Input new tag here:')

    class Meta:
        model = Image
        fields = ['image_name', 'image_text', 'image_picture', 'new_tag']
