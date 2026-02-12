from django.urls import path

from . import views

urlpatterns = [
    path("", views.template_list, name="template_list"),
    path("create/", views.template_create, name="template_create"),
    path("<int:pk>/edit/", views.template_edit, name="template_edit"),
    path("<int:pk>/delete/", views.template_delete, name="template_delete"),
    path("merge/", views.template_merge, name="template_merge"),
    path("api/search/", views.api_template_search, name="api_template_search"),
    path("api/<int:pk>/variables/", views.api_template_variables, name="api_template_variables"),
    path("api/<int:pk>/render/", views.api_template_render, name="api_template_render"),
]
