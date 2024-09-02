from django.urls import path
from . import views


app_name = 'xml_converter'
urlpatterns = [
    path('', views.index, name='index'),
    path('documents/', views.documents, name='documents'),
    path('tags/', views.tags, name='tags'),
    path('tasks/', views.tasks, name='tasks'),
    path('task_lists/', views.task_lists, name='task_lists'),
    path('task_boards/', views.task_boards, name='task_boards'),
    path('activities/', views.activities, name='activities'),
    path('time_intervals/', views.time_intervals, name='time_intervals'),
]
