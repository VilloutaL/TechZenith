from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('nuevo-usuario/', views.nuevo_usuario, name='nuevo_usuario'),
    path('obtener-usuarios/', views.obtener_usuarios),
    path("asignaturas/", views.mis_asignaturas, name= 'mis_asignaturas'),
    path('asignatura/<int:id>/', views.material_asignatura, name='material_asignatura'),
     path('asignatura/<int:asignatura_id>/subir-material/', views.subir_material, name='subir_material'),
    path('material/<int:id>/editar/', views.editar_material, name='editar_material'),
    path('material/<int:id>/borrar/', views.borrar_material, name='borrar_material'),
]