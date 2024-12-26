from django.urls import path
from . import views


app_name = 'logbook'
urlpatterns = [
    path('', views.index, name='index'),
    path('create_entry/', views.create_entry, name='create_entry'),
    path('display_entry/<int:entry_id>/', views.display_entry, name='display_entry'),
]