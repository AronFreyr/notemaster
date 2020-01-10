from django.urls import path
from . import views


app_name = 'xml_converter'
urlpatterns = [
    path('', views.index, name='index'),
    path('documents/', views.documents, name='documents'),
    path('tags/', views.tags, name='tags'),
]
