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

    test_create_imported_documents_from_xml()


def test_create_imported_documents_from_xml():
    imported_documents_list = []
    imported_tags_list = []
    with open('./notesfromxml/tests/all_docs_as_xml_test1.xml', 'r') as xml_file:
        xml_text = xml_file.read()
        #print(xml_text)
        xml_text = xml_text.replace("<?xml version='1.0' encoding='UTF-8'?>", '')
        new_xml_element = LET.ElementTree(objectify.fromstring(xml_text))
        for elem in new_xml_element.findall('./document'):
            print('--------------')
            print('NAME:', elem.name)
            print('TEXT:', elem['text'])
            imported_document = ImportedDocument(name=elem.name, text=elem['text'])

            for elem2 in elem.findall('./document_tags/document_tag'):
                print('TAG:', elem2.tag_name)
                print('TYPE:', elem2.tag_type)
                print('META_TYPE:', elem2.meta_tag_type)
                imported_tag = ImportedTag(name=elem2.tag_name, tag_type=elem2.tag_type, meta_tag_type=elem2.meta_tag_type)
                imported_document.add_tag(imported_tag)
                imported_tags_list.append(imported_tag)
            imported_documents_list.append(imported_document)
            print('---------------')
    print('length of tag list:', len(imported_tags_list))
    print('length of doc list:', len(imported_documents_list))

    for doc in imported_documents_list:
        new_doc = Document(document_name=doc.get_name(), document_text=doc.get_text())
        if not Document.objects.using('test').filter(document_name=doc.get_name()).exists():
            print('document=' + doc.get_name() + ' did not exist.')
            new_doc.save(using='test')
        new_doc = Document.objects.get(document_name=doc.get_name())

        for tag in doc.get_tags():
            print('document: ', doc.get_name())
            for x in doc.get_tags():
                print('tag:', x)
            if not Tag.objects.using('test').filter(tag_name=tag.get_name()).exists():
                new_tag = Tag(tag_name=tag.get_name(), tag_type=tag.get_tag_type(),
                              meta_tag_type=tag.get_meta_tag_type())
                print('tag=' + tag.get_name() + ' did not exist.')
                new_tag.save(using='test')
            new_tag = Tag.objects.get(tag_name=tag.get_name())
            if new_tag not in new_doc.get_all_tags():
                if not Tagmap.objects.using('test').filter(tag=new_tag, document=new_doc).exists():
                    print('newDoc: ', new_doc)
                    print('newTag: ', new_tag)
                    new_tagmap = Tagmap(tag=new_tag, document=new_doc)
                    print('tagmap=' + str(new_tagmap) + ' did not exist.')
                    new_tagmap.save(using='test')

    for tag in imported_tags_list:
        new_tag = Tag(tag_name=tag.get_name(), tag_type=tag.get_tag_type(), meta_tag_type=tag.get_meta_tag_type())
        if not Tag.objects.using('test').filter(tag_name=tag.get_name()).exists():
            print('tag=' + tag.get_name() + ' did not exist on second pass.')
            new_tag.save(using='test')


class ImportedDocument:

    text = None
    name = None
    tags = None

    def __init__(self, name, text):
        self.text = text
        self.name = name
        self.tags = []

    def get_name(self):
        return self.name

    def get_text(self):
        return self.text

    def get_tags(self):
        return self.tags

    def add_tag(self, new_tag):
        self.tags.append(new_tag)


class ImportedTag:

    name = None
    tag_type = None
    meta_tag_type = None

    def __init__(self, name, tag_type, meta_tag_type):
        self.name = name
        self.tag_type = tag_type
        self.meta_tag_type = meta_tag_type

    def get_name(self):
        return self.name

    def get_tag_type(self):
        return self.tag_type

    def get_meta_tag_type(self):
        return self.meta_tag_type
