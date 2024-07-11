from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView
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
    path('crear_anuncio/', views.crear_anuncio, name='crear_anuncio'),
    path('anuncio_creado_exitosamente/', views.anuncio_creado_exitosamente, name='anuncio_creado_exitosamente'),
    path('mis_anuncios/', views.lista_anuncios_usuario, name='lista_anuncios_usuario'),
    path('editar_anuncio/<int:pk>/', views.editar_anuncio, name='editar_anuncio'),
    path('eliminar_anuncio/<int:pk>/', views.eliminar_anuncio, name='eliminar_anuncio'),
    path('api/notificaciones/', views.cargar_notificaciones, name='api_cargar_notificaciones'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('asignatura/<int:id>/', views.material_asignatura, name='material_asignatura'),
    path('asignatura/<int:asignatura_id>/subir-material/', views.subir_material, name='subir_material'),
    path('material/<int:id>/editar/', views.editar_material, name='editar_material'),
    path('material/<int:id>/borrar/', views.borrar_material, name='borrar_material'),
    path('material/<int:id>/descargar/', views.descargar_material, name='descargar_material'),
    path('asignatura/<int:asignatura_id>/calificaciones/', views.calificaciones_asignatura, name='calificaciones_asignatura'),
    path('evaluacion/<int:evaluacion_id>/agregar-calificacion/', views.agregar_calificacion, name='agregar_calificacion'),
    path('asignatura/<int:asignatura_id>/nueva-evaluacion/', views.agregar_evaluacion, name='agregar_evaluacion'),
]
