from django.test.testcases import TestCase, override_settings
from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from lxml import etree as LET
from lxml import objectify
from django.core import serializers


class XMLToObjTestCase(TestCase):

    def setUp(self):
        pass

    # def test_read_xml(self):
    #     tree = LET.parse(r'C:\Users\aronf\my_folder\git\notemaster\notes\tests/documents_2022-01-24.xml')
    #     documents = tree.getroot()
    #     for document in documents:
    #         for child in document:
    #             if child.tag == 'name':
    #                 print(child.text)
        #print(root.tag)

    def test_get_data_from_db(self):
        test_doc = Document.objects.all()
        test_doc = Document.objects.filter(document_name='Angular Material Modules').all()
        print(test_doc)
        #for x in test_doc:
        #    print(x.document_name)

    def test_convert_objects_directly_to_xml(self):
        Document.objects.create(document_name="Java", document_text="Java document text test 1", )
        test_docs = Document.objects.all()
        # test_doc = Document.objects.filter(document_name='Angular Material Modules').all()
        test_doc = Document.objects.get(document_name='Java')

        # test_string = LET.tostring(test_doc)
        # print(test_string)
        test_string = serializers.serialize('xml', test_docs, fields=['document_name', 'document_text'])
        print(test_string)

