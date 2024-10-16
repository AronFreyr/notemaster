from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.db.models import Q
from django.views.decorators.http import require_safe
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from notes.forms import AddTagForm, CreateDocumentForm, CreateImageForm
from notes.services.object_handling import handle_new_tag, remove_object, delete_object
from notemaster.settings import CACHE_TIME
from notes.views.portal_views import *
from notes.views.dev_views import *
from notes.services.graph_generator import test_create_graph

#from .tests import turtle_graphics_tests


@require_safe  # Only allows the GET and HEAD HTTP methods through.
@login_required
# @cache_page(CACHE_TIME)  # Caching the first page is not helpful.
def index(request):
    programming_portal_tags = Tag.objects.filter(
      Q(tag_name='Programming')
      | Q(tag_name='Javascript')
      | Q(tag_name='Angular')
      | Q(tag_name='Python')
      | Q(tag_name='Amazon Web Services')
      | Q(tag_name='Spring')
      | Q(tag_name='Java')
      | Q(tag_name='git')
      | Q(tag_name='Spring Annotations')).order_by('tag_name')
    history_portal_tags = Tag.objects.filter(
        Q(tag_name='History')
        | Q(tag_name='Rome')
        | Q(tag_name='Seven Kings of Rome')
        | Q(tag_name='Roman Republic')
        | Q(tag_name='Roman Empire')
    ).order_by('tag_name')

    # turtle_graphics_tests.draw_document_map()
    #test_create_graph()

    most_recent_docs = Document.objects.exclude(tagmap__tag__meta_tag_type='task')\
                           .exclude(document_type='activity').exclude(document_type='task').order_by('-id')[:10]

    return render(request, 'notes/index.html',
                  {'programming_portal_tags': programming_portal_tags,
                   'history_portal_tags': history_portal_tags,
                   'most_recent_documents': most_recent_docs})


@login_required
@cache_page(CACHE_TIME)
def list_db_content(request):
    # TODO: Update the documentation.
    """
    Shows a list of all the documents, tags and tagmaps currently in the database.
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
        return render(request, 'notes/create-document.html',
                      {'create_document_form': CreateDocumentForm()})
    if request.method == 'POST':
        form = CreateDocumentForm(request.POST)
        if form.is_valid():
            # TODO: throw an error if the document name is blank.
            doc_name = form.cleaned_data.get('document_name')
            doc_text = form.cleaned_data.get('document_text')
            new_tag = form.cleaned_data.get('new_tag')

            if not Document.objects.filter(document_name=doc_name).exists():
                new_doc = Document(document_name=doc_name, document_text=doc_text,
                                   document_last_modified_by=request.user, document_created_by=request.user)
                new_doc.save()
                handle_new_tag(new_tag, tag_creator=request.user, new_doc=new_doc)
                return redirect(reverse('notes:display_doc', kwargs={'doc_id': new_doc.id}))
            else:  # There can not be multiple documents with the same name.
                invalid_form = CreateDocumentForm(initial={'document_name': doc_name,
                                                           'document_text': doc_text,
                                                           'new_tag': new_tag})
                duplicate_name_error = 'This name is already taken. Choose another one.'
                return render(request, 'notes/create-document.html',
                              {'create_document_form': invalid_form,
                               'duplicate_name_error': duplicate_name_error})

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
                                  image_picture=image_picture,
                                  image_created_by=request.user, image_last_modified_by=request.user)
                new_image.save()
                handle_new_tag(new_tag, new_image=new_image, tag_creator=request.user)
                return redirect(reverse('notes:display_img', kwargs={'img_id': new_image.id}))
            else:
                # TODO: Add functionality in the template to display the duplicate name error text.
                duplicate_name_error = 'This name is already taken. Choose another one.'
                return render(request, 'notes/create-image.html', {'create_image_form': form,
                                                                   'duplicate_name_error': duplicate_name_error})

    return redirect(reverse('notes:index'))


@login_required
def display_doc(request, doc_id):
    """
    Displays a single document and all of its tags.
    :param doc_id: The ID of the document that is to be displayed.
    :param request: The classic Django request object.
    :return: renders the HTML page with the document and the document text paragraphs in a list for easy display
    in the HTML.
    """
    document = Document.objects.get(id=doc_id)
    return render(request, 'notes/display-doc.html', {'document': document})


@login_required
def display_image(request, img_id):
    image = Image.objects.get(id=img_id)
    return render(request, 'notes/display-image.html', {'image': image})


@login_required
def display_tag(request, tag_id: int):
    """
    Displays a single tag.
    :param request: The request object.
    :param tag_id: The ID of the tag to be displayed.
    :return: render for the tag, which will be rendered with the display-tag.html file.
    """
    tag = Tag.objects.get(id=tag_id)
    return render(request, 'notes/display-tag.html', {'tag': tag})


@login_required
def edit_tag(request, tag_id: int):
    # TODO: Document.
    tag = Tag.objects.get(id=tag_id)
    if request.method == 'POST':
        tag.tag_last_modified_by = request.user
        if 'tag_choices' in request.POST:  # Changing the tag type.
            tag_choice = request.POST['tag_choices']
            if tag_choice == 'normal':  # Normal tags shouldn't have any meta type.
                tag.meta_tag_type = 'none'
            tag.tag_type = tag_choice

        if 'meta_tag_choices' in request.POST:  # Changing the meta tag type.
            tag.meta_tag_type = request.POST['meta_tag_choices']
        tag.save()
        return redirect(reverse('notes:display_tag', kwargs={'tag_id': tag.id}))
    return render(request, 'notes/edit-tag2.html', {'tag': tag})


@login_required
def edit_doc(request, doc_id):
    """
    Enables edits to the current document. TODO: currently it's only possible to edit the document text.
    :param request: The request object.
    :param doc_id: The ID of the document to be edited
    :return: A render of the edited document.
    """
    document = Document.objects.get(id=doc_id)
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        document.document_last_modified_by = request.user
        if form.is_valid():
            tag = form.cleaned_data.get('tag_name')
            handle_new_tag(tag, tag_creator=request.user, new_doc=document)
        if 'name_textarea_edit_document_text' in request.POST:
            new_doc_text = request.POST['name_textarea_edit_document_text']
            document.document_text = new_doc_text
            document.save()
        if 'name_type_choices' in request.POST:
            new_doc_type = request.POST['name_type_choices']
            if new_doc_type != document.document_type:
                document.document_type = new_doc_type
                document.save()
        return redirect(reverse('notes:display_doc', kwargs={'doc_id': document.id}))
    return render(request, 'notes/edit-doc2.html', {'document': document, 'form': AddTagForm()})


@login_required
def edit_image(request, img_id: int):
    """
    Enables edits to the current image. TODO: currently it's only possible to edit the image text.
    :param request: The request object.
    :param img_id: The ID of the image to be edited
    :return: A render of the edited image.
    """
    image = Image.objects.get(id=img_id)
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        image.image_last_modified_by = request.user
        if form.is_valid():
            tag = form.cleaned_data.get('tag_name')
            handle_new_tag(tag, tag_creator=request.user, new_image=image)
        if 'name_textarea_edit_image_text' in request.POST:
            new_image_text = request.POST['name_textarea_edit_image_text']
            image.image_text = new_image_text
            image.save()
        if 'name_textarea_edit_image_name' in request.POST:
            new_image_name = request.POST['name_textarea_edit_image_name']
            if new_image_name == image.image_name:
                # TODO: send error that the name is the same as the old one.
                pass
            is_name_in_use = Image.objects.filter(image_name=new_image_name).first()
            if not is_name_in_use:
                image.image_name = new_image_name
                image.save()
            else:
                # TODO: send error that the name is taken by another image.
                pass
        return redirect(reverse('notes:display_img', kwargs={'img_id': image.id}))
    return render(request, 'notes/edit-image.html', {'image': image, 'form': AddTagForm()})


@login_required
def delete_or_remove(request, obj_id: int):
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
    :param obj_id: The ID of the tag or document that should be deleted or removed.
    :return: If a tag was removed from a document while the document was being viewed, the function
    redirects to the document, else it redirects to the index.
    """
    currently_viewed_document = None
    if request.method == 'GET':
        # TODO: Throw error, you should never GET delete/remove.
        pass
    if request.method == 'POST':
        obj_type = request.POST['object_type']  # Is it a document or a tag?
        action_type = request.POST['action_type']  # Are we deleting or removing?
        if 'currently_viewed_doc' in request.POST:  # If we are viewing a document.
            #if request.POST['currently_viewed_doc'] != obj_name:  # And if that doc is not the doc we are removing.
            currently_viewed_document = Document.objects.get(document_name=request.POST['currently_viewed_doc'])
            if obj_type == 'document' and currently_viewed_document.id == obj_id:  # The doc is being deleted.
                currently_viewed_document = None

        if action_type == 'delete':
            delete_object(obj_id, obj_type, request)
        elif action_type == 'remove':
            remove_object(obj_id, obj_type, request)
        else:
            # TODO: throw error, action_type should only be delete of remove
            pass
    if currently_viewed_document is not None:
        return redirect(reverse('notes:display_doc', kwargs={'doc_id': currently_viewed_document.id}))
    return redirect(reverse('notes:index'))


@login_required
def display_search_results(request):
    items_to_display = {'documents': [], 'tags': [], 'images': []}
    if request.method == 'GET':
        item_list = [x.strip() for x in request.GET['search-bar-input'].split(',')]
        if 'advancedsearch[]' in request.GET:
            search_options = dict(request.GET)['advancedsearch[]']
            if 'documents' in search_options:  # If the check for doc search in on. Default=True.
                for item in item_list:
                    if Document.objects.filter(document_name__icontains=item).exists():
                        document_object = Document.objects.filter(document_name__icontains=item)
                        items_to_display['documents'].extend(document_object)
                items_to_display['documents'].sort(key=lambda x: x.document_name)  # Sort the doc list.

            if 'tags' in search_options:  # If the check for tag search is on. Default=False.
                for item in item_list:
                    if Tag.objects.filter(tag_name__icontains=item).exists():
                        tag_object = Tag.objects.filter(tag_name__icontains=item)
                        items_to_display['tags'].extend(tag_object)
                items_to_display['tags'].sort(key=lambda x: x.tag_name)  # Sort the tag list.

            if 'images' in search_options: # If the check for image search is on.
                for item in item_list:
                    if Image.objects.filter(image_name__icontains=item).exists():
                        image_object = Image.objects.filter(image_name__icontains=item)
                        items_to_display['images'].extend(image_object)
                items_to_display['images'].sort(key=lambda x: x.image_name)

    return render(request, 'notes/search-results.html', {'search_results': items_to_display})


@login_required
def advanced_search(request):
    """
    Returns the interface for making an advanced search. Does not return the result of the search itself.
    :param request: The request object.
    :return: The advanced-search view.
    """
    items_to_display = {'documents': [], 'tags': []}
    if request.method == 'GET':
        if 'doc-and-search' not in request.GET:
            return render(request, 'notes/advanced-search.html', {})
        else:
            print('and:', request.GET['doc-and-search'])
            doc = request.GET['doc-and-search']
            not_doc = request.GET['doc-not-search']
            if Document.objects.filter(document_name__contains=doc).exists():
                document_object = Document.objects.filter(document_name__contains=doc).exclude(document_name__exact=not_doc)
                items_to_display['documents'].extend(document_object)

            print('not:', request.GET['doc-not-search'])

            print('or:', request.GET['doc-or-search'])

            tag = request.GET['tag-and-search']
            not_tag = request.GET['tag-not-search']
            or_tag = request.GET['tag-or-search']

            if Tag.objects.filter(tag_name__contains=tag).exists():
                tag_object = Tag.objects.filter(tag_name__contains=tag)
                items_to_display['tags'].extend(tag_object)
            # TODO: return proper things.
            return render(request, 'notes/search-results.html', {'search_results': items_to_display})
