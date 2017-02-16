from django.conf.urls import url
from . import views

app_name = 'notesfromxml'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<detail>\w+)/$', views.xml_detail, name='xml_detail'),
]
