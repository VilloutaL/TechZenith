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
        AM = "AM"
        PM = "PM"
    
    class Estado(models.TextChoices):
        SIN_REGISTRAR = "S", _("Sin registrar")
        PRESENTE = "P", _("Presente")
        AUSENTE = "A", _("Ausente")
        RETRASADO = "R", _("Retrasado")

    dia = models.DateField()
    jornada = models.CharField(max_length=2, choices=Jornada)
    estado = models.CharField(max_length=1, choices=Estado)
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f'Asistencia del dia {self.dia} para el alumno {self.alumno}'

class Justificacion(models.Model):
    ID_apoderado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    certificado = models.FileField(upload_to='certificados/', null=True, blank=True)
    fecha_justificacion = models.DateField()

class AsistenciaJustificacion(models.Model):
    ID_asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE)
    ID_justificacion = models.ForeignKey(Justificacion, on_delete=models.CASCADE)


class Asignatura(models.Model):
    nombre = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='static/aulavirtual/media/', null=True, blank=True)
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
    archivo = models.FileField(upload_to ='aula_virtual/uploads/', null=True, blank=True)
    fecha_publicacion = models.DateField(auto_now_add=True, blank=True)
    
    def __str__(self):
        return self.titulo

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

