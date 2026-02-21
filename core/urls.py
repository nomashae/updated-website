from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("culture/", views.culture, name="culture"),
    path("executive-orders/", views.executive_orders, name="executive_orders"),
    path("editable-element/update/", views.editable_element_update, name="editable_element_update"),
]
