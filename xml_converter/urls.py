from django.urls import path
from . import views


app_name = 'xml_converter'
urlpatterns = [
    path('', views.index, name='index'),
    path('documents/', views.documents, name='documents'),
    path('tags/', views.tags, name='tags'),
    # path('help/', views.display_help, name='display_help'),
    # path('listdbcontent/', views.list_db_content, name='list_db_content'),
    # path('portal/<str:tag_name>/', views.display_portal, name='display_portal'),
    # path('createdoc/', views.create_doc, name='create_doc'),
]
