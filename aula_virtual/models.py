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
        PRESENTE = "P", _("Presente")
        AUSENTE = "A", _("Ausente")
        RETRASADO = "R", _("Retrasado")

    dia = models.DateField()
    jornada = models.CharField(max_length=2, choices=Jornada)
    estado = models.CharField(max_length=1, choices=Estado)
    ID_alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)

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