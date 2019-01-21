from django.test.testcases import TestCase
from ..models import Document, Tag, Tagmap
import turtle
import xml.etree.ElementTree


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
        xml_text = ''
        xml_text += '<document>\n'
        xml_text += '<name>' + test_doc.document_name + '</name>\n'
        xml_text += '<text>' + test_doc.document_text + '</text>\n'
        xml_text += '<document_tags>\n'
        for tag in test_doc.get_all_tags_sorted():
            xml_text += '<document_tag>' + tag.tag_name + '</document_tag>\n'
        xml_text += '</document_tags>\n'
        xml_text += '</document>'
        print(xml_text)
        xml_element = xml.etree.ElementTree.fromstring(xml_text)
        print(xml_element.tag)
        for child in xml_element:
            print(child.tag, child.text)

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
