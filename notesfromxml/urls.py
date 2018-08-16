from django.urls import path
from . import views


app_name = 'notesfromxml'
urlpatterns = [
    path('', views.index, name='index'),
    path('help/', views.display_help, name='display_help'),
    path('listdbcontent/', views.list_db_content, name='list_db_content'),
    path('portal/<str:tag>/', views.display_portal, name='display_portal'),
    #url(r'^(?P<detail>\w+)/$', views.xml_detail, name='xml_detail-test'),
    #path('detail/', views.xml_detail, name='xml_detail-test'),
    path('createdoc/', views.create_doc, name='create_doc'),
    path('createimg/', views.create_image, name='create_image'),
    path('displaydocs/', views.display_docs, name='display_docs'),
    path('displaytags/', views.display_tags, name='display_tags'),
    path('docbytag/', views.display_docs_with_tags, name='doc_by_tag'),
    path('displaydoc/<str:doc>/', views.display_doc, name='display_doc'),
    path('displayimg/<str:img>/', views.display_image, name='display_img'),
    path('displaytag/<str:tag_name>/', views.display_tag, name='display_tag'),
    path('displaydoc/<str:doc>/editdoc/', views.edit_doc, name='edit_doc'),
    path('displayimg/<str:image>/editimg/', views.edit_image, name='edit_image'),
    path('remove/<str:obj_name>/', views.delete_or_remove, name='remove'),
    path('showviews/', views.display_all_pages, name='show_views'),  # development stuff
    path('tests/', views.display_tests, name='display_tests'),  # development stuff
    path('springportal/', views.display_spring_portal, name='display_spring_portal')  # development stuff
]
