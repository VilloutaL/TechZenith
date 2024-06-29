from django.contrib import admin
from .models import Usuario, Token, Asistencia, Justificacion, AsistenciaJustificacion, Asignatura, RegistroAsignatura, Material, Evaluacion, Calificacion, AsignaturaEvaluacion

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Token)
admin.site.register(Asistencia)
admin.site.register(Justificacion)
admin.site.register(AsistenciaJustificacion)
admin.site.register(Asignatura)
admin.site.register(RegistroAsignatura)
admin.site.register(Material)
admin.site.register(Evaluacion)
admin.site.register(Calificacion)
admin.site.register(AsignaturaEvaluacion)