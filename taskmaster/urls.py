from django.urls import path
from . import views


app_name = 'taskmaster'
urlpatterns = [
    path('', views.index, name='index'),
    path('displayboard/<int:board_id>/', views.display_board, name='display_board'),
    path('editboard/<int:board_id>/', views.edit_board, name='edit_board'),
    path('displaytask/<int:task_id>/', views.display_task, name='display_task'),
    path('edittask/<int:task_id>/', views.edit_task, name='edit_task'),
    path('deletetask/<int:task_id>/', views.delete_task, name='delete_task'),
    path('deletelist/<int:list_id>', views.delete_list, name='delete_list'),
    path('deleteboard/<int:board_id>', views.delete_board, name='delete_board'),
]
