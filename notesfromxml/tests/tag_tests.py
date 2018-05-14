from django.test.testcases import TestCase
from notesfromxml.models import Document, Tag, Tagmap
from notesfromxml.forms import AddTagForm


class DatabaseTests(TestCase):

    def test_data_relations(self):
        Document.objects.create(document_name="Java", document_text="Java document text test 1")
        Document.objects.create(document_name="JAXB", document_text="JAXB document text test 1")
        Document.objects.create(document_name="XML", document_text="XML document text test 1")

        Tag.objects.create(tag_name="Java")
        Tag.objects.create(tag_name="JAXB")
        Tag.objects.create(tag_name="XML")

        Tagmap.objects.create(document=Document.objects.get(document_name="Java"), tag=Tag.objects.get(tag_name="Java"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="Java"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="JAXB"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="XML"))
        Tagmap.objects.create(document=Document.objects.get(document_name="XML"), tag=Tag.objects.get(tag_name="XML"))

        java_doc = Document.objects.get(document_name='Java')

        for tagmap in java_doc.tagmap_set.all():
            print(tagmap.tag.tag_name)
            for tag in tagmap.tag.tagmap_set.all():
                print(tag.document.document_name)


class FormTests(TestCase):

    def test_form_hidden_fields(self):
        f = AddTagForm()
        print(f)


class TagTests(TestCase):
    """
    General tests to see what happens when adding a tag.
    """

    def test_multi_tag_string_handling(self):
        """
        How should we handle inserting many tags at the same time?
        :return: Nothing
        """
        tags = 'tag_1; tag_2; tag 3'
        split_tags = tags.split(';')
        for tag in split_tags:
            print(tag.strip())
