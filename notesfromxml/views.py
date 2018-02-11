from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from lxml import etree
from collections import defaultdict

from .models import Document, Tag, Tagmap
import os


def index(request):
    document = Document.objects.get(document_name='JAXB')
    return render(request, 'notesfromxml/index.html', {'document': document})


# A test function to see what is required to create a document and potentially store it in a database.
def create_doc(request):
    if request.method == 'GET':
        tags = Tag.objects.all()
        documents = Document.objects.all()
        tagmaps = Tagmap.objects.all()
        return render(request, 'notesfromxml/create-doc.html', {'tags': tags, 'tagmaps': tagmaps, 'documents': documents})

    if request.method == 'POST':
        print(request.POST)
        # TODO: throw an error if the document name is blank.
        if 'docName' in request.POST:  # Document name can't be blank.
            doc_name = request.POST['docName']
            doc_text = ''
            if 'docText' in request.POST:  # Document text can be empty.
                doc_text = request.POST['docText']
            if Document.objects.filter(document_name=doc_name).exists():
                # TODO: Throw error.
                print('Document with that name already exists')
            new_doc = Document(document_name=doc_name, document_text=doc_text)
            new_doc.save()

            if 'newTag' in request.POST:  # If the user is adding a tag.
                handle_new_tag(request.POST['newTag'], new_doc)

            if 'tagchoice' in request.POST:
                tag = Tag.objects.get(id=request.POST['tagchoice'])
                print("tag: ", tag.tag_name)

    return render(request, 'notesfromxml/create-doc.html')


def display_docs(request):
    documents = Document.objects.all()
    if request.method == 'POST':
        doc_name = request.POST['current_document']
        doc = Document.objects.get(document_name=doc_name)
        tag = request.POST['newTag']
        handle_new_tag(tag, doc)
    return render(request, 'notesfromxml/displaydocs.html', {'documents': documents})


def display_tags(request):
    tags = Tag.objects.all()
    return render(request, 'notesfromxml/displaytags.html', {'tags': tags})


def display_docs_with_tags(request):
    list_of_docs_with_tags = []
    if request.method == 'POST':
        tag_list = [x.strip() for x in request.POST['searchTags'].split(',')]
        for tag in tag_list:
            if Tag.objects.filter(tag_name=tag).exists():
                tag_object = Tag.objects.get(tag_name=tag)
                docs_with_tag = Document.objects.filter(tagmap__tag=tag_object)
                list_of_docs_with_tags.extend(docs_with_tag)
    return render(request, 'notesfromxml/doc_by_tag.html', {'documents': list_of_docs_with_tags})


def handle_new_tag(new_tag, new_doc=None):
    if Tag.objects.filter(tag_name=new_tag).exists():  # If the tag already exists.
        current_tag = Tag.objects.get(tag_name=new_tag)
    else:
        current_tag = Tag(tag_name=new_tag)
        current_tag.save()
    if new_doc:
        if not Tagmap.objects.filter(tag=current_tag, document=new_doc).exists():
            new_tagmap = Tagmap(document=new_doc, tag=current_tag)
            new_tagmap.save()


def xml_detail(request, detail):
    root_dict = get_xml_file()
    detail_dict = root_dict['data'][detail]
    return render(request, 'notesfromxml/xml-category.html', {'notes': detail_dict})


# Technically this function can only get a single xml file: 'general.xml'.
def get_xml_file():
    """
    Gets the 'general.xml' file in the current directory and converts it to a Python dictionary.
    :return: the root of a Python dictionary that represents the data in an xml file.
    """
    module_dir = os.path.dirname(__file__)  # Gets the current path.
    file_path = os.path.join(module_dir, 'general.xml')  # This is so we can open general.xml in the current path.
    data = etree.parse(file_path)  # Creates a tree structure from general.xml.
    root_dict = etree_to_dict(data.getroot())  # Converts the tree structure into a dictionary.
    return root_dict


# This function was acquired from the internet.
def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d
