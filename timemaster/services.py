from datetime import timedelta, date
from typing import List

from timemaster.models import TimeInterval

def get_total_time_of_intervals(intervals: List[TimeInterval]) -> timedelta:
    total_time = timedelta(0)
    for interval in intervals:
        total_time += interval.interval_amount

    return total_time


def get_week_nr_of_date(input_date: date) -> int:
    return date.isocalendar(input_date).week
