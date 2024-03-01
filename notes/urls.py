from django.urls import path
from .views import main_views

app_name = 'notes'
urlpatterns = [
    path('', main_views.index, name='index'),
    path('help/', main_views.display_help, name='display_help'),
    path('listdbcontent/', main_views.list_db_content, name='list_db_content'),
    path('portal/<str:tag_name>/', main_views.display_portal, name='display_portal'),
    path('createdoc/', main_views.create_doc, name='create_doc'),
    path('createimg/', main_views.create_image, name='create_image'),
    path('searchresults/', main_views.display_search_results, name='search_results'),
    path('document/<str:doc>/', main_views.display_doc, name='display_doc'),
    path('image/<str:img>/', main_views.display_image, name='display_img'),
    path('tag/<str:tag_name>/', main_views.display_tag, name='display_tag'),
    path('tag/<str:tag_name>/edittag/', main_views.edit_tag, name='edit_tag'),
    path('document/<str:doc>/editdoc/', main_views.edit_doc, name='edit_doc'),
    path('image/<str:image>/editimg/', main_views.edit_image, name='edit_image'),
    path('remove/<str:obj_name>/', main_views.delete_or_remove, name='remove'),
    path('advancedsearch/', main_views.advanced_search, name='advanced_search'),
    path('showviews/', main_views.display_all_pages, name='show_views'),  # development stuff
    path('tests/', main_views.display_tests, name='display_tests'),  # development stuff
    path('homepagetest/', main_views.display_homepage_test, name='homepage_test'),  # development stuff
    path('springportal/', main_views.display_spring_portal, name='display_spring_portal'),  # development stuff
    path('angularportal/', main_views.display_angular_portal, name='display_angular_portal'),  # development stuff
    path('programmingportal/', main_views.display_programming_portal, name='display_programming_portal')  # development stuff
]
