from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.http import HttpResponse
from django.db.models import Q

from .models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from .forms import AddTagForm, CreateDocumentForm, CreateImageForm
from .services import handle_new_tag, remove_object, delete_object, parser


def index(request):
    portal_tags = Tag.objects.filter(
        Q(tag_name='History')
        | Q(tag_name='Rome')
        | Q(tag_name='Programming')
        | Q(tag_name='Javascript')
        | Q(tag_name='Spring')
        | Q(tag_name='Spring Annotations')).order_by('tag_name')
    return render(request, 'notesfromxml/index.html',
                  {'tags': portal_tags,
                   'create_document_form': CreateDocumentForm(),
                   'create_image_form': CreateImageForm()})


def display_portal(request, tag):
    portal_docs = Document.objects.filter(tagmap__tag__tag_name=tag).order_by('document_name')
    return render(request, 'notesfromxml/display-portal.html',
                  {'documents': portal_docs})


def list_db_content(request):
    # TODO: Update the documentation.
    """
    Shows a list of all of the documents, tags and tagmaps currently in the database.
    :param request: The classic Django request object.
    :return: renders the HTML page with three lists, one list of every document, one list of every tag and
    one list of every tagmap.
    """
    return render(request, 'notesfromxml/list-db-content.html',
                  {'tags': Tag.objects.all().order_by('tag_name'),
                   'tagmaps': Tagmap.objects.all(),
                   'documents': Document.objects.all().order_by('document_name'),
                   'images': Image.objects.all().order_by('image_name'),
                   'image_document_maps': ImageDocumentMap.objects.all(),
                   'image_tag_maps': ImageTagMap.objects.all(),
                   'create_document_form': CreateDocumentForm()})


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

    return redirect(reverse('notesfromxml:index'))


def create_image(request):
    if request.method == 'POST':
        form = CreateImageForm(request.POST, request.FILES)
        if form.is_valid():
            # TODO: throw an error if the document name is blank.
            image_name = form.cleaned_data.get('image_name')
            image_text = form.cleaned_data.get('image_text')
            image_picture = form.cleaned_data.get('image_picture')
            new_tag = form.cleaned_data.get('new_tag')
            # TODO: Throw error if the document already exists.
            if not Image.objects.filter(image_name=image_name).exists():
                new_image = Image(image_name=image_name, image_text=image_text,
                                  image_picture=image_picture)
                new_image.save()
                handle_new_tag(new_tag, new_image=new_image)

    return redirect(reverse('notesfromxml:index'))


def display_doc(request, doc):
    """
    Displays a single document and all of its tags.
    :param doc: The document that is to be displayed.
    :param request: The classic Django request object.
    :return: renders the HTML page with the document and the document text paragraphs in a list for easy display
    in the HTML.
    """
    document = Document.objects.get(document_name=doc)
    parsed_text = parser(document.document_text)

    return render(request, 'notesfromxml/display-doc.html',
                  {'document': document, 'document_paragraphs': parsed_text})


def display_image(request, img):
    image = Image.objects.get(image_name=img)
    return render(request, 'notesfromxml/display-image.html', {'image': image})


def display_docs(request):
    documents = Document.objects.all()
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        if form.is_valid():
            doc_name = form.cleaned_document()
            tag = form.cleaned_tag()
            doc = Document.objects.get(document_name=doc_name)
            handle_new_tag(tag, doc)

    return render(request, 'notesfromxml/display-all-docs.html',
                  {'documents': documents, 'form': AddTagForm()})


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
    :return: render for the tags, which will be rendered with the display-tags.html file.
    """
    tags = Tag.objects.all()
    return render(request, 'notesfromxml/display-tags.html', {'tags': tags})


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
    return render(request, 'notesfromxml/doc-by-tag.html', {'documents': list_of_docs_with_tags, 'form': AddTagForm()})


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
        if form.is_valid():
            tag = form.cleaned_data.get('tag_name')
            handle_new_tag(tag, new_doc=document)
        if 'name_textarea_edit_document_text' in request.POST:
            new_doc_text = request.POST['name_textarea_edit_document_text']
            document.document_text = new_doc_text
            document.save()
        return redirect(reverse('notesfromxml:display_doc', kwargs={'doc': document.document_name}))
    return render(request, 'notesfromxml/edit-doc.html', {'document': document, 'form': AddTagForm()})


def edit_image(request, image):
    """
    Enables edits to the current image. TODO: currently it's only possible to edit the image text.
    :param request: The request object.
    :param image: The image to be edited
    :return: A render of the edited image.
    """
    image = Image.objects.get(image_name=image)
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data.get('tag_name')
            handle_new_tag(tag, new_image=image)
        if 'name-textarea-edit-image-text' in request.POST:
            new_image_text = request.POST['name-textarea-edit-image-text']
            image.image_text = new_image_text
            image.save()
        return redirect(reverse('notesfromxml:display_img', kwargs={'img': image.image_name}))
    return render(request, 'notesfromxml/edit-image.html', {'image': image, 'form': AddTagForm()})


def delete_or_remove(request, obj_name):
    """
    This function deletes or removes objects from the database. It takes in a post request that uses
    the request object with obj_name to determine what kind of object it is working with and whether it
    should delete it or remove it.
    Removing an object means to disassociate it from another object, i.e. removing a tag from a document,
    it does so by deleting the tagmap between the objects.
    Deleting an object is the same as removing them except it also deletes of of the objects tagmaps as well
    as deleting the object itself.
    :param request: The Django request object. From it the function acquires the 'object_type',
    'action_type', 'currently_viewed_doc' and possibly 'currently_viewed_tag' in the future.
    :param obj_name: The name of the tag or document that should be deleted or removed.
    :return: If a tag was removed from a document while the document was being viewed, the function
    redirects to the document, else it redirects to the index.
    """
    document = None
    if request.method == 'GET':
        # TODO: Throw error, you should never GET remove.
        pass
    if request.method == 'POST':
        obj_type = request.POST['object_type']  # Is it a document or a tag?
        action_type = request.POST['action_type']  # Are we deleting or removing?
        if 'currently_viewed_doc' in request.POST:  # If we are viewing a document.
            if request.POST['currently_viewed_doc'] != obj_name:  # And if that doc is not the doc we are removing.
                document = Document.objects.get(document_name=request.POST['currently_viewed_doc'])

        if action_type == 'delete':
            delete_object(obj_name, obj_type, request)
        elif action_type == 'remove':
            remove_object(obj_name, obj_type, request)
        else:
            # TODO: throw error, action_type should only be delete of remove
            pass
    if document is not None:
        return redirect(reverse('notesfromxml:display_doc', kwargs={'doc': document.document_name}))
    return redirect(reverse('notesfromxml:index'))


# A view that displays links to all of the pages/templates that have been created in this project, this is
# for development purposes only.
def display_all_pages(request):
    return render(request, 'notesfromxml/display-all-pages.html')


# A test view that displays the stuff behind the "Test" button in the navigation bar.
def display_tests(request):
    return render(request, 'notesfromxml/tests.html')
