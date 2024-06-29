from django.contrib import admin
from .models import Usuario, Token, Asistencia, Justificacion, AsistenciaJustificacion

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Token)
admin.site.register(Asistencia)
admin.site.register(Justificacion)
admin.site.register(AsistenciaJustificacion)