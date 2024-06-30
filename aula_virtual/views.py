from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import RegistroAsignatura, Asignatura

def index(request):
    return render(request, "aula_virtual/index.html", {})

@login_required
def mis_asignaturas(request):
    usuario = request.user
    registros = RegistroAsignatura.objects.filter(usuario = usuario)
    asignaturas = [registro.asignatura for registro in registros]
    return render(request, 'aula_virtual/asignaturas.html',{'asignaturas': asignaturas})

