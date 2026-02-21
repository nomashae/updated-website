from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("culture/", views.culture, name="culture"),
    path("blog/", views.blog_feed, name="blog"),
    path("editable-element/update/", views.editable_element_update, name="editable_element_update"),
    path("api/pages/create/", views.create_dynamic_page, name="create_dynamic_page"),
    path("api/editor/upload/", views.editor_file_upload, name="editor_file_upload"),
    path("api/editor/library/", views.get_media_library, name="get_media_library"),
    path("api/blog/create/", views.api_blog_create, name="api_blog_create"),
    path("api/blog/delete/", views.api_blog_delete, name="api_blog_delete"),
    path("<slug:slug>/", views.dynamic_page, name="dynamic_page"),
]
