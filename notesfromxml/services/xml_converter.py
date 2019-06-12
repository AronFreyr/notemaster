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

    with open('./notesfromxml/tests/all_docs_as_xml_test1.xml', 'w') as xml_file:
        xml_file.write(xml_to_string)

    with open('./notesfromxml/tests/all_docs_as_xml_test1.xml', 'r') as xml_file:
        xml_text = xml_file.read()
        #print(xml_text)
        xml_text = xml_text.replace("<?xml version='1.0' encoding='UTF-8'?>", '')
        new_xml_element = LET.ElementTree(objectify.fromstring(xml_text))
        for elem in new_xml_element.findall('./document'):
            print('--------------')
            print('NAME:', elem.name)
            print('TEXT:', elem['text'])
            for elem2 in elem.findall('./document_tags/document_tag'):
                print('TAG:', elem2.tag_name)
                print('TYPE:', elem2.tag_type)
                print('META_TYPE:', elem2.meta_tag_type)
            print('---------------')
