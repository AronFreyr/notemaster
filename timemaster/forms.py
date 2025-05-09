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

class PlotTimeIntervalsInRangeForm(forms.Form):

    date_today = datetime.date.today()
    offset_time = datetime.date(year=date_today.year - 1, month=date_today.month, day=date_today.day)
    first_date = forms.DateField(initial=offset_time,
                                 widget=forms.DateInput(attrs={'type': 'date'}))
    last_date = forms.DateField(initial=date_today,
                                 widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        fields = ['first_date', 'last_date']