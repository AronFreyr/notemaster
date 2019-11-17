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

    with open('./notes/tests/all_docs_as_xml_test1.xml', 'w') as xml_file:
        xml_file.write(xml_to_string)

    test_create_imported_documents_from_xml()


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

    with open('./notes/tests/all_tags_as_xml_test1.xml', 'w') as xml_file:
        xml_file.write(xml_to_string)

    test_create_imported_tags_from_xml()


def test_create_imported_tags_from_xml():
    imported_tags_list = []
    imported_documents_list = []

    with open('./notes/tests/all_tags_as_xml_test1.xml', 'r') as xml_file:
        xml_text = xml_file.read()
        xml_text = xml_text.replace("<?xml version='1.0' encoding='UTF-8'?>", '')
        new_xml_element = LET.ElementTree(objectify.fromstring(xml_text))  # Convert XML string to elements.
        for elem in new_xml_element.findall('./tag'):  # Find all tags.
            # Create a tag object, this is not the same as the tag object that is in the database.
            imported_tag = ImportedTag(name=elem.name, tag_type=elem['tag_type'], meta_tag_type=elem['meta_tag_type'])

            for elem2 in elem.findall('./tag_documents/tag_document'):  # Find all documents for the tag.
                # Create a document object, this is not the same as the document object that is in the database.
                imported_document = ImportedDocument(name=elem2.document_name, text=elem2.document_text)
                imported_tag.add_document(imported_document)
                imported_documents_list.append(imported_document)
            imported_tags_list.append(imported_tag)

    for tag in imported_tags_list:
        if not Tag.objects.using('test').filter(tag_name=tag.get_name()).exists():
            # Create a tag object like the objects that are in the database.
            new_tag = Tag(tag_name=tag.get_name(), tag_type=tag.get_tag_type(), meta_tag_type=tag.get_meta_tag_type())
            new_tag.save(using='test')
        new_tag = Tag.objects.using('test').get(tag_name=tag.get_name())

        for doc in tag.get_documents():
            if not Document.objects.using('test').filter(document_name=doc.get_name()).exists():
                new_doc = Document(document_name=doc.get_name(), document_text=doc.get_text())
                new_doc.save(using='test')
            new_doc = Document.objects.using('test').get(document_name=doc.get_name())

            if new_doc not in new_tag.get_all_docs():  # If this document has no connection to the tag.
                # If the Tagmap does not exist (it shouldn't), create it, it serves as the connection
                # between the document and the tag.
                if not Tagmap.objects.using('test').filter(tag=new_tag, document=new_doc).exists():
                    new_tagmap = Tagmap(tag=new_tag, document=new_doc)
                    new_tagmap.save(using='test')

    # Go through all the documents just to verify that no document was missed.
    # ATTN: documents that didn't have any connections to tags will still be missed.
    for doc in imported_documents_list:
        if not Document.objects.using('test').filter(document_name=doc.get_name()).exists():
            print('document=' + doc.get_name() + ' did not exist on second pass.')
            new_doc = Document(document_name=doc.get_name(), document_text=doc.get_text())
            new_doc.save(using='test')


def test_create_imported_documents_from_xml():
    imported_documents_list = []  # A list of all the document objects that are found in the XML.
    # All of the tags that are found, this list is not complete because tags without any docs are not found.
    imported_tags_list = []
    with open('./notes/tests/all_docs_as_xml_test1.xml', 'r') as xml_file:
        xml_text = xml_file.read()
        # Get rid of the XML header.
        xml_text = xml_text.replace("<?xml version='1.0' encoding='UTF-8'?>", '')
        new_xml_element = LET.ElementTree(objectify.fromstring(xml_text))  # Convert XML string to elements.
        for elem in new_xml_element.findall('./document'):  # Find all documents.
            # Create a document object, this is not the same as the document object that is in the database.
            imported_document = ImportedDocument(name=elem.name, text=elem['text'])

            for elem2 in elem.findall('./document_tags/document_tag'):  # Find all tags for the document.
                # Create a tag object, this is not the same as the tag object that is in the database.
                imported_tag = ImportedTag(name=elem2.tag_name, tag_type=elem2.tag_type, meta_tag_type=elem2.meta_tag_type)
                imported_document.add_tag(imported_tag)
                imported_tags_list.append(imported_tag)
            imported_documents_list.append(imported_document)

    for doc in imported_documents_list:
        if not Document.objects.using('test').filter(document_name=doc.get_name()).exists():
            # Create a document object like the objects that are in the database.
            new_doc = Document(document_name=doc.get_name(), document_text=doc.get_text())
            new_doc.save(using='test')
        new_doc = Document.objects.using('test').get(document_name=doc.get_name())

        for tag in doc.get_tags():
            if not Tag.objects.using('test').filter(tag_name=tag.get_name()).exists():
                new_tag = Tag(tag_name=tag.get_name(), tag_type=tag.get_tag_type(),
                              meta_tag_type=tag.get_meta_tag_type())
                new_tag.save(using='test')
            new_tag = Tag.objects.using('test').get(tag_name=tag.get_name())

            if new_tag not in new_doc.get_all_tags():  # If this tag has no connection to the document.
                # If the Tagmap does not exist (it shouldn't), create it, it serves as the connection
                # between the document and the tag.
                if not Tagmap.objects.using('test').filter(tag=new_tag, document=new_doc).exists():
                    new_tagmap = Tagmap(tag=new_tag, document=new_doc)
                    new_tagmap.save(using='test')

    # Go through all the tags just to verify that no tag was missed.
    # ATTN: tags that didn't have any connections to documents will still be missed.
    for tag in imported_tags_list:
        if not Tag.objects.using('test').filter(tag_name=tag.get_name()).exists():
            print('tag=' + tag.get_name() + ' did not exist on second pass.')
            new_tag = Tag(tag_name=tag.get_name(), tag_type=tag.get_tag_type(), meta_tag_type=tag.get_meta_tag_type())
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
    documents = None

    def __init__(self, name, tag_type, meta_tag_type):
        self.name = name
        self.tag_type = tag_type
        self.meta_tag_type = meta_tag_type
        self.documents = []

    def get_name(self):
        return self.name

    def get_tag_type(self):
        return self.tag_type

    def get_meta_tag_type(self):
        return self.meta_tag_type

    def get_documents(self):
        return self.documents

    def add_document(self, document):
        self.documents.append(document)
