from django.test.testcases import TestCase, override_settings
from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from lxml import etree as LET
from lxml import objectify


class XMLToObjTestCase(TestCase):

    def setUp(self):
        pass

    def test_read_xml(self):
        tree = LET.parse(r'C:\Users\aronf\my_folder\git\notemaster\notes\tests/documents_2022-01-24.xml')
        documents = tree.getroot()
        for document in documents:
            for child in document:
                if child.tag == 'name':
                    print(child.text)
        #print(root.tag)

    def test_get_data_from_db(self):
        test_doc = Document.objects.all()
        test_doc = Document.objects.filter(document_name='Angular Material Modules').all()
        print(test_doc)
        #for x in test_doc:
        #    print(x.document_name)

