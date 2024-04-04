from django.test.testcases import TestCase
from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from lxml import etree as LET
from lxml import objectify


class StrangeThingsTests(TestCase):

    def setUp(self):
        pass

    def test_print(self):
        print('test printing')
