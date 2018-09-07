from django.db import models


class Document(models.Model):
    document_name = models.TextField()
    document_text = models.TextField()
    document_image = models.ImageField(blank=True)  # This allows only 1 image for each document.

    def get_parsed_text(self):
        from .services import parser
        return parser(self.document_text)

    def get_all_tags(self):
        return [tagmap.tag for tagmap in self.tagmap_set.all()]

    def get_all_tags_sorted(self):
        return [tagmap.tag for tagmap in self.tagmap_set.all().order_by('tag__tag_name')]

    def __str__(self):
        return self.document_name


class Tag(models.Model):
    tag_name = models.TextField()

    def get_nr_of_docs_with_tag(self):
        return self.tagmap_set.count()

    def __str__(self):
        return self.tag_name


class Tagmap(models.Model):
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE
    )
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return 'doc: ' + self.document.document_name + ' - tag: ' + self.tag.tag_name


class Image(models.Model):
    image_name = models.TextField(blank=True)
    image_text = models.TextField(blank=True)
    image_picture = models.ImageField(upload_to='gallery')

    def get_all_tags(self):
        return [tagmap.tag for tagmap in self.imagetagmap_set.all()]

    def get_all_tags_sorted(self):
        return [tagmap.tag for tagmap in self.imagetagmap_set.all().order_by('tag__tag_name')]

    def __str__(self):
        return self.image_name


class ImageTagMap(models.Model):
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE
    )
    image = models.ForeignKey(
        'Image',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return 'image: ' + self.image.image_name + ' - tag: ' + self.tag.tag_name


class ImageDocumentMap(models.Model):
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE
    )
    image = models.ForeignKey(
        'Image',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return 'image: ' + self.image.image_name + ' - document: ' + self.document.document_name
