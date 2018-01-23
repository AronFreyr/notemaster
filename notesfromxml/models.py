from django.db import models


class Document(models.Model):
    document_name = models.TextField()
    document_text = models.TextField()
    document_image = models.ImageField(blank=True)  # This allows only 1 image for each document.

    def __str__(self):
        return self.document_name


class Tag(models.Model):
    tag_name = models.TextField()

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
        return 'doc: ' + self.document.document_name + " - tag: " + self.tag.tag_name
