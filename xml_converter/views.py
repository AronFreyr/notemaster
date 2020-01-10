from django.http import HttpResponse

from lxml import etree as LET
from lxml import objectify
from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap


def index(request):
    pass


def documents(request):
    return HttpResponse(test_create_xml_from_documents(), content_type='text/xml')


def tags(request):
    return HttpResponse(test_create_xml_from_tags(), content_type='text/xml')


def test_create_xml_from_documents():
    test_docs = Document.objects.all()

    xml_text = '<documents>\n'
    for doc in test_docs:
        xml_text += '<document>\n'
        xml_text += '<name>' + doc.document_name + '</name>\n'
        input_text = doc.document_text
        while ']]>' in input_text:
            input_text = input_text.replace(']]>', '.\].\].\>')
        while '<![CDATA[' in input_text:
            input_text = input_text.replace('<![CDATA[', '\<!\[CDATA\[')
        xml_text += '<text> <![CDATA[' + input_text + ']]> </text>\n'
        xml_text += '<document_tags>\n'
        for tag in doc.get_all_tags_sorted():
            xml_text += '<document_tag>\n'
            xml_text += '<tag_name>' + tag.tag_name + '</tag_name>\n'
            xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
            xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
            xml_text += '</document_tag>\n'
        xml_text += '</document_tags>\n'
        xml_text += '</document>\n'
    xml_text += '</documents>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))

    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()

    #with open('./notes/tests/all_docs_as_xml_test1.xml', 'w') as xml_file:
    #    xml_file.write(xml_to_string)

    # test_create_imported_documents_from_xml()

    #return xml_element.getroot()
    return xml_to_string


def test_create_xml_from_tags():
    # Convert all of the tags in the database to XML.
    test_tags = Tag.objects.all()  # Get all of the tags.
    xml_text = '<tags>\n'
    for tag in test_tags:
        xml_text += '<tag>\n'
        xml_text += '<name>' + tag.tag_name + '</name>\n'
        xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
        xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
        xml_text += '<tag_documents>\n'
        for document in tag.get_all_docs():  # Get all docs associated with a tag.
            xml_text += '<tag_document>\n'
            xml_text += '<document_name>' + document.document_name + '</document_name>\n'
            doc_text = document.document_text
            # XML escape.
            while ']]>' in doc_text:
                doc_text = doc_text.replace(']]>', '.\].\].\>')
            while '<![CDATA[' in doc_text:
                doc_text = doc_text.replace('<![CDATA[', '\<!\[CDATA\[')
            xml_text += '<document_text> <![CDATA[' + doc_text + ']]> </document_text>\n'
            xml_text += '</tag_document>\n'
        xml_text += '</tag_documents>\n'
        xml_text += '</tag>\n'
    xml_text += '</tags>'

    print(xml_text)

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))

    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()

    # with open('./notes/tests/all_tags_as_xml_test1.xml', 'w') as xml_file:
    #     xml_file.write(xml_to_string)
    #
    # test_create_imported_tags_from_xml()

    return xml_to_string
