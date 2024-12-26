from django.db import models

from notes.models import Document


class DiaryEntry(Document):

    entry_date = models.DateField()



