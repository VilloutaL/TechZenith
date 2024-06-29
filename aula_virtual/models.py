from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
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
