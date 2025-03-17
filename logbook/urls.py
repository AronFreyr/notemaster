from django.urls import path
from . import views


app_name = 'logbook'
urlpatterns = [
    path('', views.index, name='index'),
    path('create_entry/', views.create_entry, name='create_entry'),
    path('display_all_entries/', views.display_all_entries, name='display_all_entries'),
    path('display_entry/<int:entry_id>/', views.display_entry, name='display_entry'),
    path('edit_entry/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('delete_entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
]
