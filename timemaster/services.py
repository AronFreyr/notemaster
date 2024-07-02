from datetime import timedelta, date
from typing import List

from notes.services.object_handling import handle_new_tag
from notes.models import Tag
from timemaster.models import TimeInterval, Activity

def get_total_time_of_intervals(intervals: List[TimeInterval]) -> timedelta:
    total_time = timedelta(0)
    for interval in intervals:
        total_time += interval.interval_amount

    return total_time

def convert_timedelta_to_hour_format(total_time: timedelta) -> str:

    def add_prefix_zeroes(any_number) -> str:
        any_number = str(any_number)
        if len(any_number) == 1:
            any_number = '0' + any_number
        return any_number

    total_time_seconds = total_time.total_seconds()
    total_time_hours = int(total_time_seconds // 3600)
    total_time_minutes = int((total_time_seconds // 60) - (total_time_hours * 60))
    remaining_seconds = int(total_time_seconds - (total_time_hours * 3600) - (total_time_minutes * 60))

    return str(f'{add_prefix_zeroes(total_time_hours)}:{add_prefix_zeroes(total_time_minutes)}:{add_prefix_zeroes(remaining_seconds)}')


def get_week_nr_of_date(input_date: date) -> int:
    return date.isocalendar(input_date).week


def add_interval_to_activity(interval: TimeInterval, activity: Activity, user):

    # Mark the new time measurement as an interval with a tag.
    handle_new_tag('Time Interval', new_interval=interval, tag_creator=user,
                   tag_type=('meta', 'time measurement'))
    # Give the new measurement the tag that it relates to. This makes it a measurement of this activity.
    handle_new_tag(activity.document_name, new_interval=interval, tag_creator=user,
                   tag_type=('meta', 'time measurement'))
    # Mark the activity with the tag as well.
    handle_new_tag(activity.document_name, new_doc=activity, tag_creator=user,
                   tag_type=('meta', 'time measurement'))


    # Find all tags for this activity and see if any of them are name tags of other activities.
    # Add the interval to those activities as well.
    activity_all_tags = activity.get_all_tags()
    for tag in activity_all_tags:
        related_activity_query = Activity.objects.filter(document_name=tag.tag_name, document_type='activity')
        if related_activity_query.exists():
            related_activity = related_activity_query.get()
            handle_new_tag(related_activity.document_name, new_interval=interval, tag_creator=user,
                           tag_type=('meta', 'time measurement'))
