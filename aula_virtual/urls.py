from django.urls import path


from . import views

urlpatterns = [
    path('obtener-usuarios/', views.obtener_usuarios), #JSON
    path('obtener_usuario/', views.obtener_usuario), #JSON
    path("", views.index, name="index"),
    path('logout/', views.logout_view, name='logout'),
    path("home/", views.home, name="home"),
    path('nuevo-usuario/', views.nuevo_usuario, name='nuevo_usuario'),
    path('configuracion-cuenta/<uuid:token>/', views.configuracion_cuenta, name='configuracion-cuenta'),
    path('justificar/<str:rut_alumno>', views.justificar, name="justificar"),
    path("asignaturas/", views.mis_asignaturas, name= 'mis_asignaturas'),
    path('asignatura/<int:id>/', views.material_asignatura, name='material_asignatura'),
    path('asignatura/<int:asignatura_id>/subir-material/', views.subir_material, name='subir_material'),
    path('material/<int:id>/editar/', views.editar_material, name='editar_material'),
    path('material/<int:id>/borrar/', views.borrar_material, name='borrar_material'),
    path('material/<int:id>/descargar/', views.descargar_material, name='descargar_material'),
]
