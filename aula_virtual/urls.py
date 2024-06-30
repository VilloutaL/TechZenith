from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('nuevo-usuario/', views.nuevo_usuario, name='nuevo_usuario'),
    path('obtener-usuarios/', views.obtener_usuarios),
    path("asignaturas/", views.mis_asignaturas, name= 'mis_asignaturas'),
]