from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap




@login_required
def display_portal(request, tag_name):
    portal_docs = Document.objects.filter(tagmap__tag__tag_name=tag_name).order_by('document_name')
    document_list = list(portal_docs)
    for document in document_list:
        for tag_in_doc in document.get_all_tags():
            # If we find a list meta tag, go through all of the documents and remove them from our document list.
            if tag_in_doc.meta_tag_type == 'list' and tag_name != tag_in_doc.tag_name:
                for doc_with_list_tag in tag_in_doc.get_all_docs():
                    if doc_with_list_tag.document_name != tag_in_doc.tag_name and doc_with_list_tag in document_list:
                        document_list.remove(doc_with_list_tag)
    return render(request, 'notes/display-portal.html', {'documents': document_list})

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
    angular_docs = Document.objects.filter(tagmap__tag__tag_name='Angular').order_by('document_name')
    document_list = list(angular_docs)
    for document in angular_docs:
        for tagmaps in document.tagmap_set.all():
            if tagmaps.tag.tag_name == 'Angular Decorator' and document.document_name != 'Angular Decorators':
                document_list.remove(document)
            if tagmaps.tag.tag_name == 'Angular Material Modules' and document.document_name != 'Angular Material Modules':
                document_list.remove(document)

    return render(request, 'notes/angular-portal.html', {'angular_docs': document_list})
