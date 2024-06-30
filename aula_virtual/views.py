from django.shortcuts import render
from .models import Usuario, RegistroAsignatura, Asignatura
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse
import json
import secrets
import string

def generar_contrasena(longitud):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contrasena = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return contrasena

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
    if request.method == 'POST':
        username = request.POST.get('username-registro', '')
        email = request.POST.get('email-registro', '')
        password = generar_contrasena(15)
        is_active = False
        is_staff = False
        is_superuser = False
        is_profesor = request.POST.get('isProfesor-registro', False) == 'on'
        is_alumno = request.POST.get('isAlumno-registro', False) == 'on'
        is_apoderado = request.POST.get('isApoderado-registro', False) == 'on'
        tutor_id = request.POST.get('tutor-asociado', '')

        # Crear el nuevo usuario
        usuario_nuevo = Usuario.objects.create(
            username=username,
            email=email,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        # Asignar la contraseña
        usuario_nuevo.set_password(password)
        usuario_nuevo.save()

        # Asignar el usuario al grupo correspondiente y realizar acciones específicas
        if is_alumno:
            grupo_alumnos = Group.objects.get(name='Alumnos')
            usuario_nuevo.groups.add(grupo_alumnos)
            if tutor_id:
                try:
                    tutor = Usuario.objects.get(username=tutor_id)
                    usuario_nuevo.tutor = tutor
                    usuario_nuevo.save()
                    print(f'Este usuario se registrará como Alumno y su tutor es {tutor}')
                except Usuario.DoesNotExist:
                    print(f'Tutor con username {tutor_id} no encontrado.')

        if is_apoderado:
            grupo_apoderados = Group.objects.get(name='Apoderados')
            usuario_nuevo.groups.add(grupo_apoderados)
            print("Usuario es apoderado")
        
        if is_profesor:
            grupo_profesores = Group.objects.get(name='Profesores')
            usuario_nuevo.groups.add(grupo_profesores)
            print("Usuario es profesor")

        print(f'usuario: {username}, password {password}, email: {email}, Es profesor: {is_profesor}, Es Alumno: {is_alumno}, Es Apoderado: {is_apoderado}, Tutor: {tutor_id}')
    
    return render(request, 'aula_virtual/new-user.html', {})

def index(request):
    return render(request, "aula_virtual/index.html", {})

@login_required
def mis_asignaturas(request):
    usuario = request.user
    registros = RegistroAsignatura.objects.filter(usuario = usuario)
    asignaturas = [registro.asignatura for registro in registros]
    return render(request, 'aula_virtual/asignaturas.html',{'asignaturas': asignaturas})

