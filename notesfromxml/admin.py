from django.contrib import admin

from .models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap


admin.site.register(Document)
admin.site.register(Tag)
admin.site.register(Tagmap)
admin.site.register(Image)
admin.site.register(ImageDocumentMap)
admin.site.register(ImageTagMap)
