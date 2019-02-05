from django.test.testcases import TestCase
from ..models import Document, Tag, Tagmap
import turtle
import xml.etree.ElementTree as ET
from lxml import etree as LET
from lxml import objectify


class DocumentMapperTests(TestCase):

    def setUp(self):
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

    def test_setup(self):
        """
        Test to see if it is possible to create documents, tags, tagmaps and other objects
        in the "setUp" and reference them in test cases without using "self".
        :return:
        """
        test_doc = Document.objects.get(document_name='JAXB')
        print(test_doc.document_name)

    def test_create_xml_from_document(self):
        test_doc = Document.objects.get(document_name='JAXB')
        xml_text = '<documents>\n'
        xml_text += '<document>\n'
        xml_text += '<name>' + test_doc.document_name + '</name>\n'
        xml_text += '<text>' + test_doc.document_text + '</text>\n'
        xml_text += '<document_tags>\n'
        for tag in test_doc.get_all_tags_sorted():
            xml_text += '<document_tag>' + tag.tag_name + '</document_tag>\n'
        xml_text += '</document_tags>\n'
        xml_text += '</document>\n'
        xml_text += '</documents>'

        xml_element = LET.ElementTree(objectify.fromstring(xml_text))

        xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True, encoding='UTF-8').decode()

        with open('./notesfromxml/tests/test.xml', 'w') as xml_file:
            xml_file.write(xml_to_string)

    def test_create_xml_from_documents(self):
        test_docs = Document.objects.all()

        xml_text = '<documents>\n'
        for doc in test_docs:
            xml_text += '<document>\n'
            xml_text += '<name>' + doc.document_name + '</name>\n'
            xml_text += '<text>' + doc.document_text + '</text>\n'
            xml_text += '<document_tags>\n'
            for tag in doc.get_all_tags_sorted():
                xml_text += '<document_tag>' + tag.tag_name + '</document_tag>\n'
            xml_text += '</document_tags>\n'
            xml_text += '</document>\n'
        xml_text += '</documents>'

        xml_element = LET.ElementTree(objectify.fromstring(xml_text))

        xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                     encoding='UTF-8').decode()

        with open('./notesfromxml/tests/test2.xml', 'w') as xml_file:
            xml_file.write(xml_to_string)

    def test_create_xml_from_tag(self):
        test_tag = Tag.objects.get(tag_name='JAXB')

        xml_text = '<tags>\n'
        xml_text += '<tag>\n'
        xml_text += '<name>' + test_tag.tag_name + '</name>\n'
        xml_text += '<tag_type>' + test_tag.tag_type + '</tag_type>\n'
        xml_text += '<meta_tag_type>' + test_tag.meta_tag_type + '</meta_tag_type>\n'
        xml_text += '<tagged_documents>\n'
        for doc in test_tag.get_all_docs():
            xml_text += '<tagged_document>' + doc.document_name + '</tagged_document>\n'
        xml_text += '</tagged_documents>\n'
        xml_text += '</tag>\n'
        xml_text += '</tags>\n'

        xml_element = LET.ElementTree(objectify.fromstring(xml_text))

        xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                     encoding='UTF-8').decode()
        print(xml_to_string)

    def test_create_xml_from_tags(self):
        test_tags = Tag.objects.all()

        xml_text = '<tags>\n'
        for tag in test_tags:
            xml_text += '<tag>\n'
            xml_text += '<name>' + tag.tag_name + '</name>\n'
            xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
            xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
            xml_text += '<tagged_documents>\n'
            for doc in tag.get_all_docs():
                xml_text += '<tagged_document>' + doc.document_name + '</tagged_document>\n'
            xml_text += '</tagged_documents>\n'
            xml_text += '</tag>\n'
        xml_text += '</tags>\n'

        xml_element = LET.ElementTree(objectify.fromstring(xml_text))

        xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                     encoding='UTF-8').decode()
        print(xml_to_string)

    def test_get_document_connections(self):
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

        test_doc = Document.objects.get(document_name='JAXB')

        # print(test_doc.get_all_tags())
        # for tag in test_doc.get_all_tags():
        #     for tagmap in tag.tagmap_set.all():
        #         print(tagmap.document.document_name)

        my_turtle = turtle.Turtle()
        my_screen = turtle.Screen()
        my_turtle.color('red', 'yellow')
        # my_turtle.begin_fill()
        # while True:
        #     my_turtle.write("test")
        #     my_turtle.forward(200)
        #     my_turtle.left(170)
        #     if abs(my_turtle.pos()) < 1:
        #         break
        # my_turtle.end_fill()
        # my_turtle.setpos(my_turtle.pos()[0] + 50, my_turtle.pos()[1] + 50)
        docs_and_pos = {}
        offset = (10, 20)
        for tag in test_doc.get_all_tags():
            #print(tag.tagmap_set.all())
            if tag.tagmap_set.all() is not None:
                for tagmap in tag.tagmap_set.all():
                    doc_name = tagmap.document.document_name
                    print('doc_name: ' + doc_name + ' - pos: x=' + str(my_turtle.pos()[0]) + ', y=' + str(my_turtle.pos()[1]))
                    if doc_name in docs_and_pos.keys():
                        my_turtle.setpos(docs_and_pos[doc_name]['x'], docs_and_pos[doc_name]['y'])
                    else:
                        my_turtle.forward(200 + offset[0])
                        my_turtle.left(100 + offset[1])
                        docs_and_pos[doc_name] = {'x': my_turtle.pos()[0], 'y': my_turtle.pos()[1]}
                        my_turtle.write(doc_name)

                        offset = (offset[0] + 10, offset[1] + 20)
                    print(docs_and_pos)
                #my_turtle.write(tag.tag_name)
                #my_turtle.forward(200)
                #my_turtle.left(100)
        turtle.done()
