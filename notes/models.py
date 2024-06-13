from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    document_name = models.TextField()
    document_text = models.TextField()

    document_created = models.DateTimeField(auto_now_add=True)
    document_modified = models.DateTimeField(auto_now=True)
    document_created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='document_created_by',
                                            blank=True, null=True)
    document_last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='document_last_modified_by',
                                             blank=True, null=True)

    DOCUMENT_CHOICES = (
        ('document', 'Document'),
        ('task', 'Task'),
        ('activity', 'Activity'),
    )

    document_type = models.TextField(
        choices=DOCUMENT_CHOICES,
        default='document',
    )


    def get_parsed_text(self):
        from .services.parser import TextParser
        parser = TextParser()
        return parser.perform_parse(self.document_text)

    def get_all_tags(self):
        return [tagmap.tag for tagmap in self.tagmap_set.all()]

    def get_all_tags_sorted(self):
        return [tagmap.tag for tagmap in self.tagmap_set.all().order_by('tag__tag_name')]

    def __str__(self):
        return self.document_name


class Tag(models.Model):

    TAG_TYPE_CHOICES = (
        ('normal', 'Normal'),
        ('meta', 'Meta')
    )

    META_TAG_TYPE_CHOICES = (
        ('list', 'List'),
        ('task', 'Task'),
        ('none', 'None'),
        ('time measurement', 'Time Measurement'),
    )

    tag_created = models.DateTimeField(auto_now_add=True)
    tag_modified = models.DateTimeField(auto_now=True)

    tag_created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tag_created_by',
                                            blank=True, null=True)
    tag_last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                                  related_name='tag_last_modified_by',
                                                  blank=True, null=True)

    tag_name = models.TextField()

    tag_type = models.TextField(
        choices=TAG_TYPE_CHOICES,
        default='normal'
    )

    meta_tag_type = models.TextField(
        choices=META_TAG_TYPE_CHOICES,
        default='none'
    )

    def get_nr_of_docs_with_tag(self):
        return self.tagmap_set.count()

    def get_all_docs(self):
        return [tagmap.document for tagmap in self.tagmap_set.all()]

    def __str__(self):
        return self.tag_name


class Tagmap(models.Model):
    """
    Table connecting the Document table to the Tag table.
    """
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

    image_created = models.DateTimeField(auto_now_add=True)
    image_modified = models.DateTimeField(auto_now=True)

    image_created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='image_created_by',
                                            blank=True, null=True)
    image_last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                                  related_name='image_last_modified_by',
                                                  blank=True, null=True)

    def get_parsed_text(self):
        from .services.parser import TextParser
        parser = TextParser()
        return parser.perform_parse(self.image_text)

    def get_all_tags(self):
        return [tagmap.tag for tagmap in self.imagetagmap_set.all()]

    def get_all_tags_sorted(self):
        return [tagmap.tag for tagmap in self.imagetagmap_set.all().order_by('tag__tag_name')]

    def __str__(self):
        return self.image_name


class ImageTagMap(models.Model):
    """
    Table connecting the Image table to the Tag table.
    """
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
    """
    Table connecting the Image table to the Document table.
    """
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
