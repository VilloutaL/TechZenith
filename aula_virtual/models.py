from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid


class Usuario(AbstractUser):
    tutor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='alumnos')

    def __str__(self):
        if self.first_name == "":
            return self.username
        return self.first_name

class Token(models.Model):
    token_autenticacion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dead_time = models.DateTimeField()
    ID_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def is_expired(self):
        return timezone.now() > self.dead_time

    def __str__(self):
        return str(self.token_autenticacion)

class Asistencia(models.Model):
    class Jornada(models.TextChoices):
        AM = "AM", _("Mañana")
        PM = "PM", _("Tarde")
    
    class Estado(models.TextChoices):
        PRESENTE = "P", _("Presente")
        AUSENTE = "A", _("Ausente")
        RETRASADO = "R", _("Retrasado")

    dia = models.DateField()
    jornada = models.CharField(max_length=2, choices=Jornada.choices)
    estado = models.CharField(max_length=1, choices=Estado.choices)
    ID_alumno = models.ForeignKey('Usuario', on_delete=models.CASCADE)

    def __str__(self):
        return f'Asistencia del dia {self.dia} para el alumno {self.ID_alumno}'

class Justificacion(models.Model):
    ID_apoderado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    certificado = models.FileField()
    fecha_justificacion = models.DateField()

class AsistenciaJustificacion(models.Model):
    ID_asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE)
    ID_justificacion = models.ForeignKey(Justificacion, on_delete=models.CASCADE)


class Asignatura(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    
class RegistroAsignatura(models.Model):
    ROLES =(
        ('ALUMNO','alumno'),
        ('PROFESOR','profesor'),
    )    
    asignatura = models.ForeignKey(Asignatura,on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.CharField(max_length= 10 , choices=ROLES)
    
class Material(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete= models.CASCADE)
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    archivo = models.FileField()
    fecha_publicacion = models.DateField()

class Evaluacion(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_termino = models.DateTimeField()
    tipo = models.CharField(max_length=50)


class Calificacion(models.Model):
    ID_usuario = models.ForeignKey(Usuario, on_delete= models.CASCADE)
    ID_evaluacion = models.ForeignKey(Evaluacion, on_delete= models.CASCADE)
    comentario = models.TextField()
    calificacion = models.FloatField()

class AsignaturaEvaluacion(models.Model):
    ID_evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    ID_asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)   

class Anuncio(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    profesor_id = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    esta_eliminado = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
    
class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
