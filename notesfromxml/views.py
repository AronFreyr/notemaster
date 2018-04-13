from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.http import HttpResponse
from lxml import etree
from collections import defaultdict
import os

from .models import Document, Tag, Tagmap
from .forms import AddTagForm


def index(request):
    tags = Tag.objects.all()
    documents = Document.objects.all()
    tagmaps = Tagmap.objects.all()
    return render(request, 'notesfromxml/index.html', {'tags': tags, 'tagmaps': tagmaps, 'documents': documents})


# A test function to see what is required to create a document and potentially store it in a database.
def create_doc(request):
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

    return redirect(reverse('notesfromxml:index'))


def display_doc(request, doc):
    """
    Displays a single document and all of its tags.
    For testing purposes, also displays all documents connected to the tag og the original document.
    :param doc: The document that is to be displayed.
    :param request: The classic Django request object.
    :return: renders the HTML page with the document and the document text paragraphs in a list for easy display
    in the HTML.
    """
    document = Document.objects.get(document_name=doc)
    return render(request, 'notesfromxml/display-doc.html',
                  {'document': document, 'document_paragraphs': document.document_text.split('\n')})


def display_docs(request):
    documents = Document.objects.all()
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data.get('tag_name')
            doc_name = form.cleaned_data.get('current_document')
            doc = Document.objects.get(document_name=doc_name)

            handle_new_tag(tag, doc)
    return render(request, 'notesfromxml/displaydocs.html', {'documents': documents, 'form': AddTagForm()})


def display_tag(request, tag_name):
    """
    Displays a single tag.
    :param request: The request object.
    :param tag_name: The name of the tag to be displayed.
    :return: render for the tag, which will be rendered with the display-tag.html file.
    """
    tag = Tag.objects.get(tag_name=tag_name)
    return render(request, 'notesfromxml/display-tag.html', {'tag': tag})


def display_tags(request):
    """
    Displays all of the tags.
    :param request: the request object.
    :return: render for the tags, which will be rendered with the displaytags.html file.
    """
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


def edit_doc(request, doc):
    """
    Enables edits to the current document. TODO: currently it's only possible to edit the document text.
    :param request: The request object.
    :param doc: The document to be edited
    :return: A render of the edited document.
    """
    document = Document.objects.get(document_name=doc)
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        print(form)
        if form.is_valid():
            tag = form.cleaned_data.get('tag_name')
            print(tag)
            handle_new_tag(tag, document)
        if 'name_textarea_edit_document_text' in request.POST:
            new_doc_text = request.POST['name_textarea_edit_document_text']
            document.document_text = new_doc_text
            document.save()
        return redirect(reverse('notesfromxml:display_doc', kwargs={'doc': document.document_name}))
    return render(request, 'notesfromxml/edit-doc.html', {'document': document, 'form': AddTagForm()})


def delete(request, obj_name):
    document = None
    if request.method == 'GET':
        # TODO: Throw error, you should never GET delete.
        pass
    if request.method == 'POST':
        object_type = request.POST['object_type']
        if object_type == 'tag':  # If we are deleting a tag.
            tag_to_delete = Tag.objects.get(tag_name=obj_name)
            for tagmap in tag_to_delete.tagmap_set.all():
                tagmap.delete()
            tag_to_delete.delete()
            if 'currently_viewed_doc' in request.POST:
                document = Document.objects.get(document_name=request.POST['currently_viewed_doc'])
        elif object_type == 'document':  # If we are deleting a document.
            doc_to_delete = Document.objects.get(document_name=obj_name)
            for tagmap in doc_to_delete.tagmap_set.all():
                tagmap.delete()
            doc_to_delete.delete()
    if document is not None:
        return render(request, 'notesfromxml/display-doc.html', {'document': document})
    return redirect(reverse('notesfromxml:index'))


def remove(request, obj_name):
    if request.method == 'GET':
        # TODO: Throw error, you should never GET remove.
        pass
    if request.method == 'POST':
        object_type = request.POST['object_type']
        if object_type == 'tag':  # If we are removing a tag.
            tag_to_remove = Tag.objects.get(tag_name=obj_name)
            current_document = Document.objects.get(document_name=request.POST['currently_viewed_doc'])
            tagmap_to_delete = tag_to_remove.tagmap_set.get(tag=tag_to_remove, document=current_document)
            tagmap_to_delete.delete()
        elif object_type == 'document':
            doc_to_remove = Document.objects.get(document_name=obj_name)
            current_tag = Tag.objects.get(tag_name=request.POST['currently_viewed_tag'])
            tagmap_to_delete = doc_to_remove.tagmap_set.get(tag=current_tag, document=doc_to_remove)
            tagmap_to_delete.delete()
    return redirect(reverse('notesfromxml:index'))


def handle_new_tag(new_tag, new_doc=None):
    """
    Function for handling the creation of new tags, adding them to the document and saving them in the database.
    :param new_tag: A tag that is to be added to a document. The tag may already be in the database but not yet associated
    with the document that we want to link it to.
    :param new_doc: If we are creating a new document at the same time we are creating a new tag, we need to create a new
    tagmap as well.
    :return: nothing.
    """
    if Tag.objects.filter(tag_name=new_tag).exists():  # If the tag already exists.
        current_tag = Tag.objects.get(tag_name=new_tag)
    else:  # Create the new tag and save it in the database.
        current_tag = Tag(tag_name=new_tag)
        current_tag.save()
    if new_doc:  # If we are adding a tag to a newly created document.
        # If the tagmap for the newly created document and the tag does not exist.
        if not Tagmap.objects.filter(tag=current_tag, document=new_doc).exists():
            new_tagmap = Tagmap(document=new_doc, tag=current_tag)
            new_tagmap.save()


# TODO: Can be removed.
def test_redirect(request):
    return redirect(reverse('notesfromxml:index'))


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
