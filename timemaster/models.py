from django.db import models

from notes.models import Document, Tag


class Activity(Document):
    pass


class TimeInterval(models.Model):
    interval_date = models.DateField()
    interval_amount = models.DurationField()

    def get_all_tags(self):
        return [tagmap.tag for tagmap in self.intervaltagmap_set.all()]

    def get_all_tags_sorted(self):
        return [tagmap.tag for tagmap in self.intervaltagmap_set.all().order_by('tag__tag_name')]


class IntervalTagMap(models.Model):
    """
    Table connecting the TimeInterval table to the Tag table.
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    interval = models.ForeignKey(
        'TimeInterval',
        on_delete=models.CASCADE
    )

    # def __str__(self):
    #     return 'image: ' + self.image.image_name + ' - tag: ' + self.tag.tag_name
