from django.urls import path
from . import views

app_name = 'notesfromxml'
urlpatterns = [
    path('', views.index, name='index'),
    path('help/', views.display_help, name='display_help'),
    path('listdbitems/', views.list_docs_tags_tagmaps, name='list_docs_tags_tagmaps'),
    path('portal/<str:tag>/', views.display_portal, name='display_portal'),
    #url(r'^(?P<detail>\w+)/$', views.xml_detail, name='xml_detail-test'),
    #path('detail/', views.xml_detail, name='xml_detail-test'),
    path('createdoc/', views.create_doc, name='create_doc'),
    path('displaydocs/', views.display_docs, name='display_docs'),
    path('displaytags/', views.display_tags, name='display_tags'),
    path('docbytag/', views.display_docs_with_tags, name='doc_by_tag'),
    path('displaydoc/<str:doc>/', views.display_doc, name='display_doc'),
    path('displaytag/<str:tag_name>/', views.display_tag, name='display_tag'),
    path('displaydoc/<str:doc>/editdoc/', views.edit_doc, name='edit_doc'),
    path('delete/<str:obj_name>/', views.delete, name='delete'),
    path('remove/<str:obj_name>/', views.remove, name='remove'),
    path('showviews/', views.display_all_pages, name='show_views'),  # development stuff
    path('tests/', views.display_tests, name='display_tests')  # development stuff
]
