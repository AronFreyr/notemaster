from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from .forms import AddTagForm, CreateDocumentForm, CreateImageForm
from .services.object_handling import handle_new_tag, remove_object, delete_object
from .services.xml_converter import test_create_xml_from_documents, test_create_xml_from_tags  # Test for xml object conversion
from .services.graph_generator import test_create_graph

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

    return render(request, 'notes/index.html',
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
    return render(request, 'notes/display-portal.html',
                  {'documents': document_list})


# A test function to create a test homepage.
@login_required
def display_homepage_test(request):

    latest_programming_documents = Document.objects.filter(tagmap__tag__tag_name='Programming').order_by('-id')[:5]
    latest_history_documents = Document.objects.filter(tagmap__tag__tag_name='History').order_by('-id')[:5]

    return render(request, 'notes/homepage-test.html',
                  {'latest_programming_docs': latest_programming_documents,
                   'latest_history_docs': latest_history_documents})


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
    return render(request, 'notes/spring-portal.html', {'documents': document_list,
                                                               'spring_projects': spring_project_docs})


# A test function for seeing how individual portals could work.
@login_required
def display_programming_portal(request):
    programming_languages_docs = Document.objects.filter(tagmap__tag__tag_name='Programming Language').order_by('document_name')
    return render(request, 'notes/programming-portal.html',
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

    return render(request, 'notes/angular-portal.html', {'angular_docs': document_list})


@login_required
def list_db_content(request):
    # TODO: Update the documentation.
    """
    Shows a list of all of the documents, tags and tagmaps currently in the database.
    :param request: The classic Django request object.
    :return: renders the HTML page with three lists, one list of every document, one list of every tag and
    one list of every tagmap.
    """
    return render(request, 'notes/list-db-content.html',
                  {'tags': Tag.objects.all().order_by('tag_name'),
                   'tagmaps': Tagmap.objects.all(),
                   'documents': Document.objects.all().order_by('document_name'),
                   'images': Image.objects.all().order_by('image_name'),
                   'image_document_maps': ImageDocumentMap.objects.all(),
                   'image_tag_maps': ImageTagMap.objects.all()})


@login_required
def display_help(request):
    return render(request, 'notes/help.html')


@login_required
def create_doc(request):
    if request.method == 'GET':
        return render(request, 'notes/create-document.html', {'create_document_form': CreateDocumentForm()})
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
                return render(request, 'notes/display-doc.html', {'document': new_doc})

    return redirect(reverse('notes:index'))


@login_required
def create_image(request):
    if request.method == 'GET':
        return render(request, 'notes/create-image.html', {'create_image_form': CreateImageForm()})
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

    return redirect(reverse('notes:index'))


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
    return render(request, 'notes/display-doc.html', {'document': document})


@login_required
def display_image(request, img):
    image = Image.objects.get(image_name=img)
    return render(request, 'notes/display-image.html', {'image': image})


@login_required
def display_tag(request, tag_name):
    """
    Displays a single tag.
    :param request: The request object.
    :param tag_name: The name of the tag to be displayed.
    :return: render for the tag, which will be rendered with the display-tag.html file.
    """
    tag = Tag.objects.get(tag_name=tag_name)
    return render(request, 'notes/display-tag.html', {'tag': tag})


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
        return redirect(reverse('notes:display_tag', kwargs={'tag_name': tag.tag_name}))
    return render(request, 'notes/edit-tag.html', {'tag': tag})


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
        return redirect(reverse('notes:display_doc', kwargs={'doc': document.document_name}))
    return render(request, 'notes/edit-doc.html', {'document': document, 'form': AddTagForm()})


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
        return redirect(reverse('notes:display_img', kwargs={'img': image.image_name}))
    return render(request, 'notes/edit-image.html', {'image': image, 'form': AddTagForm()})


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
        # TODO: Throw error, you should never GET delete/remove.
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
        return redirect(reverse('notes:display_doc', kwargs={'doc': document.document_name}))
    return redirect(reverse('notes:index'))


@login_required
def display_search_results(request):
    items_to_display = {'documents': [], 'tags': []}
    if request.method == 'GET':
        item_list = [x.strip() for x in request.GET['search-bar-input'].split(',')]
        if 'advancedsearch[]' in request.GET:
            search_options = dict(request.GET)['advancedsearch[]']
            if 'documents' in search_options:  # If the check for doc search in on. Default=True.
                for item in item_list:
                    if Document.objects.filter(document_name__contains=item).exists():
                        document_object = Document.objects.filter(document_name__contains=item)
                        items_to_display['documents'].extend(document_object)
                items_to_display['documents'].sort(key=lambda x: x.document_name)  # Sort the doc list.

            if 'tags' in search_options:  # If the check for tag search is on. Default=False.
                for item in item_list:
                    if Tag.objects.filter(tag_name__contains=item).exists():
                        tag_object = Tag.objects.filter(tag_name__contains=item)
                        items_to_display['tags'].extend(tag_object)
                items_to_display['tags'].sort(key=lambda x: x.tag_name)  # Sort the tag list.

    return render(request, 'notes/search-results.html', {'search_results': items_to_display})


# A view that displays links to all of the pages/templates that have been created in this project, this is
# for development purposes only.
@login_required
def display_all_pages(request):
    return render(request, 'notes/display-all-pages.html')


# A test view that displays the stuff behind the "Test" button in the navigation bar.
@login_required
def display_tests(request):

    #test_create_xml_from_documents()
    test_create_xml_from_tags()
    #test_create_graph()
    messages.add_message(request, messages.INFO, 'test message')
    return render(request, 'notes/tests.html')
