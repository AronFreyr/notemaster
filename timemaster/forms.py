from django import forms
import datetime

from timemaster.models import TimeInterval, Activity
from notes.forms import AddTagForm


class AddActivityForm(forms.Form):

    activity_name = forms.CharField(label='Input the activity name here')
    activity_description = forms.CharField(label='Input the activity description here', required=False)

    class Meta:
        fields = ['activity_name', 'activity_description']


class AddTimeIntervalForm(forms.ModelForm):

    interval_date = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={'type': 'date'}))
    #interval_amount = forms.IntegerField(min_value=0)
    interval_amount = forms.CharField(widget=forms.TimeInput(attrs={'type': 'time', 'step': '1', 'value': '00:00:00'}))

    class Meta:
        model = TimeInterval
        fields = ['interval_date', 'interval_amount']

class AddTagToIntervalForm(AddTagForm):

    current_time_interval = forms.CharField(widget=forms.HiddenInput(),
                                       required=False)  # The time interval that the tag gets added to.

    def cleaned_time_interval(self):
        return self.cleaned_data['current_time_interval']