from django.utils import timezone
from django.test.testcases import TestCase
from notes.models import Document, Tag, Tagmap


class DocumentManipulationTestCase(TestCase):
    """
    Tests to see if the Documents are created and connected correctly.
    """

    def setUp(self):
        Document.objects.create(document_name="Java", document_text="Java document text test 1")
        Tag.objects.create(tag_name="Java")
        Tagmap.objects.create(document=Document.objects.get(document_name="Java"), tag=Tag.objects.get(tag_name="Java"))

    def test_document_tag_connection(self):
        java_doc = Document.objects.get(document_name='Java')
        for tagmap in java_doc.tagmap_set.all():
            self.assertEqual(tagmap.tag.tag_name, "Java")

    def test_create_document(self):

        current_date_and_time = timezone.now()
        doc = Document.objects.create(document_name="Python", document_text="Python document text test 1",
                                      document_created_by=None, document_last_modified_by=None)
        self.assertEqual(doc.document_name, "Python")
        self.assertEqual(doc.document_text, "Python document text test 1")
        self.assertEqual(doc.document_type, 'document')
        self.assertEqual(doc.document_created.date(), current_date_and_time.date())
        self.assertEqual(doc.document_modified.date(), current_date_and_time.date())

    def test_create_document_with_tag(self):
        doc = Document.objects.create(document_name="JavaScript", document_text="JavaScript document text test 1",
                                      document_created_by=None, document_last_modified_by=None)
        tag = Tag.objects.create(tag_name="JavaScript", tag_created_by=None, tag_last_modified_by=None)
        Tagmap.objects.create(document=doc, tag=tag)

        self.assertEqual(doc.tagmap_set.count(), 1)
        self.assertEqual(doc.tagmap_set.first().tag.tag_name, "JavaScript")

        self.assertEqual(doc.get_all_tags(), [tag])
        self.assertEqual(doc.get_nr_of_tags(), 1)

    def test_create_document_with_multiple_tags(self):
        doc = Document.objects.create(document_name="HTML", document_text="HTML document text test 1",
                                      document_created_by=None, document_last_modified_by=None)
        tag1 = Tag.objects.create(tag_name="HTML", tag_created_by=None, tag_last_modified_by=None)
        tag2 = Tag.objects.create(tag_name="Web Development", tag_created_by=None, tag_last_modified_by=None)
        Tagmap.objects.create(document=doc, tag=tag1)
        Tagmap.objects.create(document=doc, tag=tag2)

        self.assertEqual(doc.tagmap_set.count(), 2)
        self.assertIn(tag1, doc.get_all_tags())
        self.assertIn(tag2, doc.get_all_tags())
        self.assertEqual(doc.get_nr_of_tags(), 2)


class TagManipulationTestCase(TestCase):
    """
    Tests to see if the tags are created and connected correctly.
    """

    def setUp(self):
        Tag.objects.create(tag_name="Test Tag", tag_created_by=None, tag_last_modified_by=None)

    def test_create_tag(self):
        tag = Tag.objects.create(tag_name="Java")
        self.assertEqual(tag.tag_name, "Java")
        self.assertEqual(tag.tag_type, 'normal')
        self.assertEqual(tag.meta_tag_type, 'none')

    def test_get_nr_of_docs_with_tag(self):
        tag = Tag.objects.create(tag_name="Java")
        tag = Tag.objects.get(tag_name="Java")
        self.assertEqual(tag.get_nr_of_docs_with_tag(), 0)
