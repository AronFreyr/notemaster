from django import forms
from tinymce.widgets import TinyMCE
import datetime

from .models import DiaryEntry


class CreateDiaryEntryForm(forms.ModelForm):
    #document_name = forms.CharField(label='Document name:')
    document_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    document_text = forms.CharField(label='Document text:', widget=TinyMCE())
    new_tag = forms.CharField(label='Document tags:')
    entry_date = forms.DateField(label='Entry date:', initial=datetime.date.today,
                                 widget=forms.DateInput(attrs={'type': 'date'}))
    created_by = forms.CharField(widget=forms.HiddenInput(), required=False)
    document_type = forms.CharField(widget=forms.HiddenInput(), required=True, initial='diary_entry')

    class Meta:
        model = DiaryEntry
        fields = ['document_name', 'document_text', 'new_tag', 'entry_date', 'document_type']
