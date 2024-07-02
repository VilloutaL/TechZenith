from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario, RegistroAsignatura, Asignatura, Material
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import json
from django.core.exceptions import PermissionDenied



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



def index(request):
    return render(request, "aula_virtual/index.html", {})

@login_required
def mis_asignaturas(request):
    usuario = request.user
    registros = RegistroAsignatura.objects.filter(usuario = usuario)
    asignaturas = [registro.asignatura for registro in registros]
    return render(request, 'aula_virtual/asignaturas.html',{'asignaturas': asignaturas})


@login_required
def material_asignatura(request, id):
    asignatura = get_object_or_404(Asignatura, id=id)
    materiales = Material.objects.filter(asignatura_id=asignatura)

    es_profesor = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='PROFESOR').exists()
    es_alumno = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='ALUMNO').exists()

    if not es_profesor and not es_alumno:
        raise PermissionDenied

    context = {
        'asignatura': asignatura,
        'materiales': materiales,
        'es_profesor': es_profesor,
        'es_alumno': es_alumno
    }


    return render(request, 'aula_virtual/material_asignatura.html', context)



@login_required
def subir_material(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)

    es_profesor = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='PROFESOR').exists()
    if not es_profesor:
        raise PermissionDenied 
    

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        archivo = request.FILES['archivo']

        material = Material(
            asignatura=asignatura,
            profesor=request.user,
            titulo=titulo,
            descripcion=descripcion,
            archivo=archivo

        )
        material.save()
        return redirect('material_asignatura', id=asignatura_id)

    return render(request, 'aula_virtual/subir_material.html', {'asignatura': asignatura})

@login_required
def editar_material(request, id):
    material = get_object_or_404(Material, id=id)

    es_profesor = RegistroAsignatura.objects.filter(asignatura_id=material.asignatura_id, usuario=request.user, rol='PROFESOR').exists()
    if not es_profesor:
        raise PermissionDenied

    if request.method == 'POST':
        material.titulo = request.POST.get('titulo')
        material.descripcion = request.POST.get('descripcion')
        if 'archivo' in request.FILES:
            material.archivo = request.FILES['archivo']
        material.save()
        return redirect('material_asignatura', id=material.asignatura.id)

    return render(request, 'aula_virtual/editar_material.html', {'material': material})

@login_required
def borrar_material(request, id):
    material = get_object_or_404(Material, id=id)

    es_profesor = RegistroAsignatura.objects.filter(asignatura_id=material.asignatura_id, usuario=request.user, rol='PROFESOR').exists()
    if not es_profesor:
        raise PermissionDenied

    if request.method == 'POST':
        material.delete()
        return redirect('material_asignatura', id=material.asignatura.id)
    return render(request, 'aula_virtual/borrar_material.html', {'material': material})

