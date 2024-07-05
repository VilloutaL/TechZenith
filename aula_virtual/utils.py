from .models import Notificacion
from aula_virtual.models import Usuario, Notificacion, RegistroAsignatura

def enviar_notificacion_a_alumnos(anuncio):
    # Obtén la asignatura del anuncio
    asignatura = anuncio.asignatura
    
    # Obtén todos los usuarios que son alumnos y están inscritos en la asignatura específica
    alumnos = obtener_alumnos_de_asignatura(asignatura)

    # Enviar notificación a cada alumno
    for alumno in alumnos:
        Notificacion.objects.create(
            usuario=alumno,
            mensaje=f'Se ha publicado un nuevo anuncio en la asignatura {asignatura.nombre}: {anuncio.titulo}'
        )

def obtener_alumnos_de_asignatura(asignatura):
    # Filtrar los registros de asignatura para obtener los usuarios que son alumnos
    registros = RegistroAsignatura.objects.filter(asignatura=asignatura, rol='ALUMNO')
    
    # Obtener los usuarios (alumnos) asociados a esos registros
    alumnos = [registro.usuario for registro in registros]
    
    return alumnos