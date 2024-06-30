from django.shortcuts import render
from .models import Usuario
from django.contrib.auth.models import Group
from django.http import JsonResponse
import json

def obtener_usuarios(request):
    grupo_nombre = request.GET.get('rol', '')
    
    if grupo_nombre:
        try:
            grupo_apoderado = Group.objects.get(name=grupo_nombre)
            usuarios = list(Usuario.objects.filter(groups=grupo_apoderado).values('username', 'first_name', 'last_name'))
        except Group.DoesNotExist:
            usuarios = []  # En caso de que el grupo no exista, retornar una lista vacía
    else:
        usuarios = list(Usuario.objects.all().values('username', 'first_name', 'last_name'))
    
    return JsonResponse(usuarios, safe=False)


def index(request):
    return render(request, "aula_virtual/index.html", {})

def nuevo_usuario(request):
    
    return render(request, 'aula_virtual/new-user.html', {})