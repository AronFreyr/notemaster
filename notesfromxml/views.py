from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.http import HttpResponse

from .models import Document, Tag, Tagmap
from .forms import AddTagForm, CreateDocumentForm
from .services import handle_new_tag


def index(request):
    return render(request, 'notesfromxml/index.html', {'tags': Tag.objects.all(),
                                                       'tagmaps': Tagmap.objects.all(),
                                                       'documents': Document.objects.all(),
                                                       'form': CreateDocumentForm()})


def display_help(request):
    return render(request, 'notesfromxml/help.html')


def create_doc(request):
    if request.method == 'POST':
        print(request.POST)
        form = CreateDocumentForm(request.POST)
        if form.is_valid():
            # TODO: throw an error if the document name is blank.
            doc_name = form.cleaned_data.get('document_name')
            doc_text = form.cleaned_data.get('document_text')
            new_tag = form.cleaned_data.get('new_tag')
            # TODO: Throw error if the document already exists.
            if not Document.objects.filter(document_name=doc_name).exists():
                new_doc = Document(document_name=doc_name, document_text=doc_text)
                new_doc.save()
                handle_new_tag(new_tag, new_doc)
        # # TODO: throw an error if the document name is blank.
        # if 'docName' in request.POST:  # Document name can't be blank.
        #     doc_name = request.POST['docName']
        #     doc_text = ''
        #     if 'docText' in request.POST:  # Document text can be empty.
        #         doc_text = request.POST['docText']
        #     if Document.objects.filter(document_name=doc_name).exists():
        #         # TODO: Throw error.
        #         print('Document with that name already exists')
        #     new_doc = Document(document_name=doc_name, document_text=doc_text)
        #     new_doc.save()
        #
        #     if 'newTag' in request.POST:  # If the user is adding a tag.
        #         handle_new_tag(request.POST['newTag'], new_doc)

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
            doc_name = form.cleaned_document()
            tag = form.cleaned_tag()
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
    """
    Takes string from the template, that string is a comma separated list of tag names, and searches for any
    documents that have those tags. Then sends the document list to the template for display.
    :param request: The request object, has the comma separated string that comes from the template.
    :return: A list of all of the documents that have the tags that were in the comma separated string.
    """
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


# TODO: Can be removed.
def test_redirect(request):
    return redirect(reverse('notesfromxml:index'))
