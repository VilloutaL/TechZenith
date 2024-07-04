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
]

