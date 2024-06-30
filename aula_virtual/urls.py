from django.urls import path

from . import views

urlpatterns = [
    path('obtener-usuarios/', views.obtener_usuarios), #JSON
    path('obtener_usuario/', views.obtener_usuario), #JSON
    path("", views.index, name="index"),
    path('nuevo-usuario/', views.nuevo_usuario, name='nuevo_usuario'),
    path("asignaturas/", views.mis_asignaturas, name= 'mis_asignaturas'),
]