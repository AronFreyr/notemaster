from django.test.testcases import TestCase
from notesfromxml.models import Document, Tag, Tagmap
from notesfromxml.services import tagged_docs_to_list_parser


class TaggedDocsToListTests(TestCase):

    def test_doc_to_list_function(self):
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

        text_to_parse = 'lorem ipsum [list[[Java]]] ipsum lorem.'
        tagged_docs_to_list_parser(text_to_parse)
