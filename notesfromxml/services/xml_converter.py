from lxml import etree as LET
from lxml import objectify

from ..models import Document, Tag, Tagmap


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
            xml_text += '<document_tag>' + tag.tag_name + '</document_tag>\n'
        xml_text += '</document_tags>\n'
        xml_text += '</document>\n'
    xml_text += '</documents>'


    xml_element = LET.ElementTree(objectify.fromstring(xml_text))

    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()

    with open('./notesfromxml/tests/all_docs_as_xml_test1.xml', 'w') as xml_file:
        xml_file.write(xml_to_string)

    with open('./notesfromxml/tests/all_docs_as_xml_test1.xml', 'r') as xml_file:
        xml_text = xml_file.read()
        print(xml_text)
        xml_text = xml_text.replace("<?xml version='1.0' encoding='UTF-8'?>", '')
        new_xml_element = LET.ElementTree(objectify.fromstring(xml_text))
        root = new_xml_element.getroot()
        #print(new_xml_element)
        for child in root:
            print(child.tag)
            print(child[0].tag)
            for child0 in child:
                print(child0.tag)
        #print(xml_file.read())
        #LET.ElementTree(objectify)
