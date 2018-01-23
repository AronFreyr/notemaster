from django.contrib import admin

from .models import Document, Tag, Tagmap


admin.site.register(Document)
admin.site.register(Tag)
admin.site.register(Tagmap)
