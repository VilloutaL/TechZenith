from .models import Notificacion
from django.contrib.auth.models import User

def enviar_notificacion_a_alumnos(anuncio):
    # Obtén los usuarios que sean alumnos
    alumnos = User.objects.filter(groups__name='alumnos')

    # Crea una notificación para cada alumno
    for alumno in alumnos:
        Notificacion.objects.create(
            usuario=alumno,
            mensaje=f'Se ha publicado un nuevo anuncio: {anuncio.titulo}'
        )