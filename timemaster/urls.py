from django.urls import path
from . import views


app_name = 'timemaster'
urlpatterns = [
    path('', views.index, name='index'),
    path('displayactivity/<int:activity_id>/', views.display_activity, name='display_activity'),
    path('editactivity/<int:activity_id>/', views.edit_activity, name='edit_activity'),
    path('deleteactivity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('displayinterval/<int:interval_id>/', views.display_interval, name='display_interval'),
    path('editinterval/<int:interval_id>/', views.edit_interval, name='edit_interval'),
    path('deleteinterval/<int:interval_id>/', views.delete_interval, name='delete_interval'),
    path('removeintervaltag/<int:tag_id>/', views.remove_interval_tag, name='remove_interval_tag'),
    path('removetag/<int:obj_id>', views.remove_tag, name='remove_tag'),
    path('intervalgraph/', views.display_interval_graph, name='display_interval_graph'),
    # path('displayboard/<int:board_id>/', views.display_board, name='display_board'),
    # path('editboard/<int:board_id>/', views.edit_board, name='edit_board'),
    # path('displaytask/<int:task_id>/', views.display_task, name='display_task'),
    # path('edittask/<int:task_id>/', views.edit_task, name='edit_task'),
    # path('deletetask/<int:task_id>/', views.delete_task, name='delete_task'),
    # path('deletelist/<int:list_id>', views.delete_list, name='delete_list'),
    # path('deleteboard/<int:board_id>', views.delete_board, name='delete_board'),
]
