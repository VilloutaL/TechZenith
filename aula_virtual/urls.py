from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("asignaturas/", views.mis_asignaturas, name= 'mis_asignaturas'),
]