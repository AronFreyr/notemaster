from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from .forms import AddTagForm, CreateDocumentForm, CreateImageForm
from .services.object_handling import handle_new_tag, remove_object, delete_object

from .tests import turtle_graphics_tests


@login_required
def index(request):
    programming_portal_tags = Tag.objects.filter(
      Q(tag_name='Programming')
      | Q(tag_name='Javascript')
      | Q(tag_name='Angular')
      | Q(tag_name='Python')
      | Q(tag_name='Amazon Web Services')
      | Q(tag_name='Spring')
      | Q(tag_name='Spring Annotations')).order_by('tag_name')
    history_portal_tags = Tag.objects.filter(
        Q(tag_name='History')
        | Q(tag_name='Rome')
        | Q(tag_name='Seven Kings of Rome')
        | Q(tag_name='Roman Republic')
        | Q(tag_name='Roman Empire')
    ).order_by('tag_name')

    # turtle_graphics_tests.draw_document_map()

    return render(request, 'notesfromxml/index.html',
                  {'programming_portal_tags': programming_portal_tags,
                   'history_portal_tags': history_portal_tags})


@login_required
def display_portal(request, tag_name):
    portal_docs = Document.objects.filter(tagmap__tag__tag_name=tag_name).order_by('document_name')
    document_list = list(portal_docs)
    for document in document_list:
        for tag_in_doc in document.get_all_tags():
            # If we find a list meta tag, go through all of the documents and remove them from our
            # document list.
            if tag_in_doc.meta_tag_type == 'list' and tag_name != tag_in_doc.tag_name:
                for doc_with_list_tag in tag_in_doc.get_all_docs():
                    if doc_with_list_tag.document_name != tag_in_doc.tag_name and doc_with_list_tag in document_list:
                        document_list.remove(doc_with_list_tag)
    return render(request, 'notesfromxml/display-portal.html',
                  {'documents': document_list})


# A test function to create a test homepage.
@login_required
def display_homepage_test(request):
    return render(request, 'notesfromxml/homepage-test.html')


# A test function for seeing how individual portals could work.
@login_required
def display_spring_portal(request):
    spring_project_docs = Document.objects.filter(tagmap__tag__tag_name='Spring Project').order_by('document_name')
    spring_docs = Document.objects.filter(tagmap__tag__tag_name='Spring').order_by('document_name')
    document_list = list(spring_docs)
    for document in spring_docs:
        if document in spring_project_docs:
            document_list.remove(document)
        for tagmaps in document.tagmap_set.all():
            if tagmaps.tag.tag_name == 'Spring Annotations' and document.document_name != 'Spring Annotations':
                document_list.remove(document)
                break
    return render(request, 'notesfromxml/spring-portal.html', {'documents': document_list,
                                                               'spring_projects': spring_project_docs})


# A test function for seeing how individual portals could work.
@login_required
def display_programming_portal(request):
    programming_languages_docs = Document.objects.filter(tagmap__tag__tag_name='Programming Language').order_by('document_name')
    return render(request, 'notesfromxml/programming-portal.html',
                  {'programming_languages_docs': programming_languages_docs})


# A test function for seeing how individual portals could work.
@login_required
def display_angular_portal(request):
    angular_docs = Document.objects.filter(tagmap__tag__tag_name='Angular').order_by(
        'document_name')
    document_list = list(angular_docs)
    for document in angular_docs:
        for tagmaps in document.tagmap_set.all():
            if tagmaps.tag.tag_name == 'Angular Decorator' and document.document_name != 'Angular Decorators':
                document_list.remove(document)
            if tagmaps.tag.tag_name == 'Angular Material Modules' and document.document_name != 'Angular Material Modules':
                document_list.remove(document)
    return render(request, 'notesfromxml/angular-portal.html',
                  {'angular_docs': document_list})


@login_required
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
                   'image_tag_maps': ImageTagMap.objects.all()})


@login_required
def display_help(request):
    return render(request, 'notesfromxml/help.html')


@login_required
def create_doc(request):
    if request.method == 'GET':
        return render(request, 'notesfromxml/create-document.html', {'create_document_form': CreateDocumentForm()})
    if request.method == 'POST':
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


@login_required
def create_image(request):
    if request.method == 'GET':
        return render(request, 'notesfromxml/create-image.html', {'create_image_form': CreateImageForm()})
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


@login_required
def display_doc(request, doc):
    """
    Displays a single document and all of its tags.
    :param doc: The document that is to be displayed.
    :param request: The classic Django request object.
    :return: renders the HTML page with the document and the document text paragraphs in a list for easy display
    in the HTML.
    """
    document = Document.objects.get(document_name=doc)
    return render(request, 'notesfromxml/display-doc.html', {'document': document})


@login_required
def display_image(request, img):
    image = Image.objects.get(image_name=img)
    return render(request, 'notesfromxml/display-image.html', {'image': image})


# TODO: This view may be unnecessary and may possible be removed.
@login_required
def display_docs(request):
    return render(request, 'notesfromxml/display-all-docs.html', {'documents': Document.objects.all()})


@login_required
def display_tag(request, tag_name):
    """
    Displays a single tag.
    :param request: The request object.
    :param tag_name: The name of the tag to be displayed.
    :return: render for the tag, which will be rendered with the display-tag.html file.
    """
    tag = Tag.objects.get(tag_name=tag_name)
    return render(request, 'notesfromxml/display-tag.html', {'tag': tag})


@login_required
def display_tags(request):
    """
    Displays all of the tags.
    :param request: the request object.
    :return: render for the tags, which will be rendered with the display-tags.html file.
    """
    tags = Tag.objects.all()
    return render(request, 'notesfromxml/display-tags.html', {'tags': tags})


@login_required
def edit_tag(request, tag_name):
    # TODO: Document.
    tag = Tag.objects.get(tag_name=tag_name)
    if request.method == 'POST':
        if 'tag_choices' in request.POST:  # Changing the tag type.
            tag_choice = request.POST['tag_choices']
            if tag_choice == 'normal':  # Normal tags shouldn't have any meta type.
                tag.meta_tag_type = 'none'
            tag.tag_type = tag_choice

        if 'meta_tag_choices' in request.POST:  # Changing the meta tag type.
            tag.meta_tag_type = request.POST['meta_tag_choices']
        tag.save()
        return redirect(reverse('notesfromxml:display_tag', kwargs={'tag_name': tag.tag_name}))
    return render(request, 'notesfromxml/edit-tag.html', {'tag': tag})


@login_required
def display_docs_with_tags(request):
    """
    Takes string from the template, that string is a comma separated list of tag names, and searches for any
    documents that have those tags. Then sends the document list to the template for display.
    :param request: The request object, has the comma separated string that comes from the template.
    :return: A list of all of the documents that have the tags that were in the comma separated string.
    """
    list_of_docs_with_tags = []
    if request.method == 'POST':
        tag_list = [x.strip() for x in request.POST['search-bar-input'].split(',')]
        for tag in tag_list:
            if Tag.objects.filter(tag_name=tag).exists():
                tag_object = Tag.objects.get(tag_name=tag)
                docs_with_tag = Document.objects.filter(tagmap__tag=tag_object)
                list_of_docs_with_tags.extend(docs_with_tag)
    return render(request, 'notesfromxml/doc-by-tag.html', {'documents': list_of_docs_with_tags})


@login_required
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


@login_required
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


@login_required
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
@login_required
def display_all_pages(request):
    return render(request, 'notesfromxml/display-all-pages.html')


# A test view that displays the stuff behind the "Test" button in the navigation bar.
@login_required
def display_tests(request):

    messages.add_message(request, messages.INFO, 'test message')
    return render(request, 'notesfromxml/tests.html')
