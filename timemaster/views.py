from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from datetime import datetime, timedelta

from timemaster import forms
from timemaster.models import Activity, TimeInterval, IntervalTagMap
from notes.services.object_handling import handle_new_tag
from notes.models import Tag
from notes.forms import AddTagForm


@login_required
def index(request):

    if request.method == 'POST':
        activity_form = forms.AddActivityForm(request.POST)
        if activity_form.is_valid():
            activity_name = activity_form.cleaned_data.get('activity_name')
            if not Activity.objects.filter(document_name=activity_name).exists():
                activity_description = activity_form.cleaned_data.get('activity_description')
                new_activity = Activity(document_name=activity_name, document_text=activity_description,
                                        document_last_modified_by=request.user, document_created_by=request.user)
                new_activity.save()
            else:
                # TODO: need to do something if the activity already exists.
                pass
    activity_form = forms.AddActivityForm()
    activities = Activity.objects.all()
    return render(request, 'timemaster/index.html',
                  {'all_activities': activities, 'activity_form': activity_form})

@login_required
def display_activity(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    if request.method == 'POST':
        interval_form = forms.AddTimeIntervalForm(request.POST)
        if interval_form.is_valid():
            interval_date = interval_form.cleaned_data.get('interval_date')
            interval_amount = interval_form.cleaned_data.get('interval_amount')
            time = datetime.strptime(interval_amount, '%H:%M:%S')
            new_timedelta = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
            new_interval = TimeInterval(interval_date=interval_date, interval_amount=new_timedelta)
            new_interval.save()

            # Mark the new time measurement as an interval with a tag.
            handle_new_tag('Time Interval', new_interval=new_interval, tag_creator=request.user,
                           tag_type=('meta', 'time measurement'))
            # Give the new measurement the tag that it relates to. This makes it a measurement of this activity.
            handle_new_tag(activity.document_name, new_interval=new_interval, tag_creator=request.user,
                           tag_type=('meta', 'time measurement'))
            # Mark the activity with the tag as well.
            handle_new_tag(activity.document_name, new_doc=activity, tag_creator=request.user,
                           tag_type=('meta', 'time measurement'))

    interval_form = forms.AddTimeIntervalForm()

    all_intervals = TimeInterval.objects.filter(intervaltagmap__tag__tag_name=activity.document_name,
                                                intervaltagmap__tag__tag_type='meta',
                                                intervaltagmap__tag__meta_tag_type='time measurement').all()
    all_seconds = 0
    for x in all_intervals:
        all_seconds += x.interval_amount.seconds
        print(x.interval_date.day)
    print(all_seconds)
    return render(request, 'timemaster/display-activity.html', {'activity': activity,
                                                                'interval_form': interval_form,
                                                                'all_intervals': all_intervals})
@login_required
def edit_activity(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    if request.method == 'POST':
        add_tag_form = AddTagForm(request.POST)
        if add_tag_form.is_valid():
            tag = add_tag_form.cleaned_data.get('tag_name')
            if tag != '':
                handle_new_tag(tag, new_doc=activity, tag_creator=request.user)

        if 'name_textarea_edit_activity_name' in request.POST:
            new_activity_name = request.POST['name_textarea_edit_activity_name']
            if new_activity_name != activity.document_name:
                activity.document_name = new_activity_name

        if 'name_textarea_edit_activity_text' in request.POST:
            new_activity_text = request.POST['name_textarea_edit_activity_text']
            if new_activity_text != activity.document_text:
                activity.document_text = new_activity_text

        activity.save()
        return redirect(reverse('timemaster:display_activity', args=(activity_id,)))

    return render(request, 'timemaster/edit-activity.html',{'activity': activity,
                                                            'add_tag_form': AddTagForm()})


@login_required
def delete_activity(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    pass


@login_required
def display_interval(request, interval_id):
    interval = TimeInterval.objects.get(id=interval_id)
    return render(request, 'timemaster/display-interval.html', {'interval': interval})


@login_required
def edit_interval(request, interval_id):
    interval = TimeInterval.objects.get(id=interval_id)

    if request.method == 'POST':
        interval_form = forms.AddTimeIntervalForm(request.POST)
        add_tag_form = forms.AddTagToIntervalForm(request.POST)
        if interval_form.is_valid():
            interval_date = interval_form.cleaned_data.get('interval_date')
            interval_amount = interval_form.cleaned_data.get('interval_amount')
            time = datetime.strptime(interval_amount, '%H:%M:%S')
            new_timedelta = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)

            if interval_date != interval.interval_date:
                interval.interval_date = interval_date
            if new_timedelta != interval.interval_amount:
                interval.interval_amount = new_timedelta

        if add_tag_form.is_valid():
            new_tags = add_tag_form.cleaned_tag()
            handle_new_tag(new_tags, new_interval=interval, tag_creator=request.user,
                           tag_type=('meta', 'time measurement'))
        interval.save()
        return redirect(reverse('timemaster:display_interval', args=(interval_id, )))

    interval_form = forms.AddTimeIntervalForm(initial={'interval_date': interval.interval_date,
                                                       'interval_amount': interval.interval_amount})
    return render(request, 'timemaster/edit-interval.html', {'interval': interval,
                                                             'interval_form': interval_form,
                                                             'add_tag_form': forms.AddTagToIntervalForm()})

@login_required
def delete_interval(request, interval_id):
    interval = TimeInterval.objects.get(id=interval_id)
    interval.delete()
    return redirect(reverse('timemaster:index'))

@login_required
def remove_interval_tag(request, tag_id):
    if request.method == 'GET':
        # todo what to do
        pass

    if request.method == 'POST':
        interval_id = request.POST['currently_viewed_interval']
        action_type = request.POST['action_type']
        object_type = request.POST['object_type']

        interval = TimeInterval.objects.get(id=interval_id)
        tag = Tag.objects.get(id=tag_id)
        interval_tag_map = IntervalTagMap.objects.get(tag=tag, interval=interval)
        interval_tag_map.delete()

        return redirect(reverse('timemaster:display_interval', args=(interval_id, )))