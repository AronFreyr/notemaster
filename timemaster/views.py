from datetime import datetime, timedelta
import plotly as py
import plotly.graph_objs as go

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, reverse

from notes.forms import AddTagForm
from notes.models import Tag
from notes.services.object_handling import handle_new_tag, remove_object
from timemaster import forms, services
from timemaster.models import Activity, TimeInterval, IntervalTagMap


@login_required
def index(request):

    if request.method == 'POST':
        activity_form = forms.AddActivityForm(request.POST)
        if activity_form.is_valid():
            activity_name = activity_form.cleaned_data.get('activity_name')
            if not Activity.objects.filter(document_name=activity_name).exists():
                activity_description = activity_form.cleaned_data.get('activity_description')
                new_activity = Activity(document_name=activity_name, document_text=activity_description,
                                        document_last_modified_by=request.user, document_created_by=request.user,
                                        document_type='activity')
                new_activity.save()
                # create new tag for the new activity.
                handle_new_tag(activity_name, new_doc=new_activity, tag_creator=request.user,
                               tag_type=('meta', 'time measurement'))
            else:
                # TODO: need to do something if the activity already exists.
                pass
    activity_form = forms.AddActivityForm()
    activities = Activity.objects.all()
    return render(request, 'timemaster/index.html',
                  {'all_activities': activities, 'activity_form': activity_form})

@login_required
def display_activity(request, activity_id: int):
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

            services.add_interval_to_activity(new_interval, activity, request.user)

    interval_form = forms.AddTimeIntervalForm()

    all_intervals = (TimeInterval.objects.filter(intervaltagmap__tag__tag_name=activity.document_name,
                                                intervaltagmap__tag__tag_type='meta',
                                                intervaltagmap__tag__meta_tag_type='time measurement')
                     .all().order_by('interval_date'))

    total_time = services.convert_timedelta_to_hour_format(services.get_total_time_of_intervals(all_intervals))

    years = all_intervals.order_by('interval_date__year').values_list('interval_date__year', flat=True).distinct()
    months = all_intervals.order_by('interval_date__month').values_list('interval_date__month', flat=True).distinct()
    weeks = all_intervals.order_by('interval_date__week').values_list('interval_date__week', flat=True).distinct()

    year_time_list, month_time_list, week_time_list = {}, {}, {}
    for year in years:
        this_year_intervals = all_intervals.filter(interval_date__year=year)
        year_time_list[year] = services.convert_timedelta_to_hour_format(
            services.get_total_time_of_intervals(this_year_intervals))

        for month in months:
            this_month_intervals = all_intervals.filter(interval_date__month=month, interval_date__year=year)
            if this_month_intervals.exists():
                month_time_list[str(month) + '-' + str(year)] = services.convert_timedelta_to_hour_format(
                    services.get_total_time_of_intervals(this_month_intervals))

        for week in weeks:
            this_week_intervals = all_intervals.filter(interval_date__week=week, interval_date__year=year)
            if this_week_intervals.exists():
                week_time_list[str(week) + '-' + str(year)] = services.convert_timedelta_to_hour_format(
                    services.get_total_time_of_intervals(this_week_intervals))

    return render(request, 'timemaster/display-activity.html', {'activity': activity,
                                                                'interval_form': interval_form,
                                                                'all_intervals': all_intervals,
                                                                'total_time': total_time,
                                                                'total_year_time': year_time_list,
                                                                'total_month_time': month_time_list,
                                                                'total_week_time': week_time_list})
@login_required
def edit_activity(request, activity_id: int):
    activity = Activity.objects.get(id=activity_id)

    if request.method == 'POST':
        add_tag_form = AddTagForm(request.POST)
        if add_tag_form.is_valid():
            tag = add_tag_form.cleaned_data.get('tag_name')
            if tag != '':
                handle_new_tag(tag, new_doc=activity, tag_creator=request.user)

            # If the new tag is a tag for another activity, give all intervals that this activity has the
            # same activity as the new tag.
            connected_activity = Activity.objects.filter(document_name=tag).first()
            if connected_activity:
                all_intervals = (TimeInterval.objects.filter(intervaltagmap__tag__tag_name=activity.document_name,
                                                             intervaltagmap__tag__tag_type='meta',
                                                             intervaltagmap__tag__meta_tag_type='time measurement')
                                 .all().order_by('interval_date'))
                for interval in all_intervals:
                    handle_new_tag(tag, new_interval=interval, tag_creator=request.user,
                                   tag_type=('meta', 'time measurement'))

        if 'name_textarea_edit_activity_name' in request.POST:
            new_activity_name = request.POST['name_textarea_edit_activity_name']
            if new_activity_name != activity.document_name:
                # todo: do something if the activity name already exists, it causes intervals to merge in unexpected ways.
                associated_name_tag = Tag.objects.get(tag_name=activity.document_name, meta_tag_type='time measurement',
                                          tag_type='meta')
                associated_name_tag.tag_name = new_activity_name
                associated_name_tag.save()
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
def delete_activity(request, activity_id: int):
    # We need to delete the activity, the name tag associated with the activity and all intervals
    # that have no other activity than this one.

    activity = Activity.objects.get(id=activity_id)

    all_intervals = (TimeInterval.objects.filter(intervaltagmap__tag__tag_name=activity.document_name,
                                                 intervaltagmap__tag__tag_type='meta',
                                                 intervaltagmap__tag__meta_tag_type='time measurement')
                     .all().order_by('interval_date'))

    if all_intervals.exists():

        # Intervals that are connected to no other activity than the one we want to delete should also be deleted.
        for interval in all_intervals:
            this_interval_activity_list = []
            for tag in interval.get_all_tags():
                activity_query = Activity.objects.filter(document_name=tag.tag_name,
                                                         document_type='activity')
                if activity_query.exists():
                    found_activity = activity_query.get()
                    if found_activity != activity:
                        this_interval_activity_list.append(activity)
            if len(this_interval_activity_list) == 0:
                interval.delete()

    associated_name_tag_query = Tag.objects.filter(tag_name=activity.document_name, meta_tag_type='time measurement',
                                                   tag_type='meta')
    if associated_name_tag_query.exists():
        associated_name_tag = associated_name_tag_query.get()
        associated_name_tag.delete()
    activity.delete()
    return redirect(reverse('timemaster:index'))


@login_required
def display_interval(request, interval_id: int):
    interval = TimeInterval.objects.get(id=interval_id)

    all_connected_activities = []
    all_tags = interval.get_all_tags()
    for tag in all_tags:
        activity_query = Activity.objects.filter(document_name=tag.tag_name)
        if activity_query.exists():
            activity = activity_query.get()
            all_connected_activities.append(activity)

    return render(request, 'timemaster/display-interval.html', {'interval': interval,
                                                                'connected_activities': all_connected_activities})


@login_required
def edit_interval(request, interval_id: int):
    interval = TimeInterval.objects.get(id=interval_id)

    all_connected_activities = []
    all_tags = interval.get_all_tags()
    for tag in all_tags:
        activity_query = Activity.objects.filter(document_name=tag.tag_name)
        if activity_query.exists():
            activity = activity_query.get()
            all_connected_activities.append(activity)

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

    current_interval_value = str(interval.interval_amount)
    if len(current_interval_value) == 7:
        # This means that the value is like this: '1:00:00' when it should be like this: '01:00:00'.
        # We add the trailing zero.
        current_interval_value = '0' + current_interval_value
    interval_form = forms.AddTimeIntervalForm(initial={'interval_date': interval.interval_date,
                                                       'interval_amount': current_interval_value})
    return render(request, 'timemaster/edit-interval.html', {'interval': interval,
                                                             'interval_form': interval_form,
                                                             'add_tag_form': forms.AddTagToIntervalForm(),
                                                             'connected_activities': all_connected_activities})

@login_required
def delete_interval(request, interval_id):
    interval = TimeInterval.objects.get(id=interval_id)
    interval.delete()
    return redirect(reverse('timemaster:index'))

@login_required
def remove_interval_tag(request, tag_id: int):
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


@login_required()
def remove_tag(request, obj_id):
    if request.method == 'GET':
        # todo what to do
        pass

    if request.method == 'POST':
        current_activity_name = request.POST['currently_viewed_doc']
        current_activity = Activity.objects.get(document_name=current_activity_name)
        tag_to_remove = Tag.objects.get(id=obj_id)
        # If we are removing a tag that belongs to a different activity from this activity, then all
        # intervals that are connected to this activity should not be connected to the other activity anymore.
        if (tag_to_remove.tag_type == 'meta' and tag_to_remove.meta_tag_type == 'time measurement' and
                current_activity.document_name != tag_to_remove.tag_name):
            connected_activity = Activity.objects.filter(document_name=tag_to_remove.tag_name).first()
            if connected_activity:
                current_activity_intervals = (TimeInterval.objects.filter(
                    intervaltagmap__tag__tag_name=current_activity.document_name,
                    intervaltagmap__tag__tag_type='meta',
                    intervaltagmap__tag__meta_tag_type='time measurement')
                    .all().order_by('interval_date'))
                for interval in current_activity_intervals:
                    interval_tag_map = IntervalTagMap.objects.filter(tag=tag_to_remove, interval=interval).first()
                    if interval_tag_map:
                        interval_tag_map.delete()

        # Remove the tag from the current activity
        remove_object(tag_to_remove.id, 'tag', request)
        return redirect(reverse('timemaster:edit_activity', kwargs={'activity_id': current_activity.id}))

@login_required()
def display_interval_graph(request):
    # Same as saying:
    # TimeInterval.objects.raw('SELECT id, interval_date, SUM(interval_amount) as my_sum
    # FROM timemaster_TimeInterval GROUP BY interval_date;'
    # )
    all_intervals = (TimeInterval.objects.values('interval_date').annotate(interval_sum=Sum('interval_amount')).order_by())

    time_interval_form = forms.PlotTimeIntervalsInRangeForm(request.GET)
    if time_interval_form.is_valid():
        first_date = time_interval_form.cleaned_data.get('first_date')
        last_date = time_interval_form.cleaned_data.get('last_date')
        all_intervals = all_intervals.filter(interval_date__range=[first_date, last_date])
    else:
        time_interval_form = forms.PlotTimeIntervalsInRangeForm()
        all_intervals = all_intervals.filter(interval_date__range=[time_interval_form.offset_time,
                                                                   time_interval_form.date_today])


    sums = [x['interval_sum'].total_seconds() // 60 / 60 for x in all_intervals]
    dates = [x['interval_date'] for x in all_intervals]
    bar_chart = go.Bar(x=dates, y=sums)
    fig = go.Figure(data=[bar_chart])
    plot_as_div = py.offline.plot(fig, include_plotlyjs=True, output_type='div')
    return render(request, 'timemaster/display-interval-graph.html',
                  {'graph': plot_as_div, 'time_interval_form': time_interval_form})
