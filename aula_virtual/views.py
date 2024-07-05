from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Usuario, RegistroAsignatura, Asignatura, Token, Asistencia, AsistenciaJustificacion
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.core.mail import send_mail
from .forms import AnuncioForm
from .models import Anuncio
from .models import Notificacion
import json
from datetime import datetime
from django.urls import reverse
from urllib.parse import urlencode
import secrets
from django.contrib.auth.decorators import login_required
import string
import uuid

def cargar_notificaciones(request):
    usuario = request.user
    notificaciones = Notificacion.objects.filter(usuario=usuario)
    data = list(notificaciones.values('id', 'mensaje', 'fecha_creacion'))
    return JsonResponse(data, safe=False)

@login_required
def crear_anuncio(request):
    if request.method == 'POST':
        form = AnuncioForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            # Obtiene la instancia del usuario actual autenticado
            usuario_actual = request.user
            
            # Asigna la instancia del usuario como profesor_id del anuncio
            form.profesor_id = usuario_actual
            form.save()
            # Redirige a una URL específica después de crear el anuncio
            return redirect('lista_anuncios_usuario')  # Define esta URL según tu necesidad
    else:
        form = AnuncioForm()

    return render(request, 'aula_virtual/crear_anuncio.html', {'form': form})

def editar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    if request.method == 'POST':
        form = AnuncioForm(request.POST, instance=anuncio)
        if form.is_valid():
            form.save()
            return redirect('lista_anuncios_usuario')
    else:
        form = AnuncioForm(instance=anuncio)
    
    return render(request, 'aula_virtual/editar_anuncio.html', {'form': form})

def eliminar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    if request.method == 'POST':
        anuncio.delete()
        return redirect('lista_anuncios_usuario')
    
    return render(request, 'aula_virtual/confirmar_eliminar_anuncio.html', {'anuncio': anuncio})

def lista_anuncios_usuario(request):
    # Obtén todos los anuncios creados por el usuario actual
    anuncios = Anuncio.objects.filter(profesor_id=request.user)
    
    # Puedes ordenar los anuncios por fecha de publicación si lo deseas
    anuncios = anuncios.order_by('-fecha_publicacion')
    
    return render(request, 'aula_virtual/lista_anuncios.html', {'anuncios': anuncios})

def anuncio_creado_exitosamente(request):
    return render(request, 'aula_virtual/anuncio_creado_exitosamente.html')

# Funciones de uso general
def generar_contrasena(longitud):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contrasena = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return contrasena

def construir_url_gestion_asistencia(fecha, jornada, id_asignatura=None, rut_alumno=None):
    # Construir la URL base con parámetros obligatorios
    url = reverse('gestion_asistencia', args=[fecha, jornada])

    # Agregar parámetros opcionales si están definidos
    query_params = {}
    if id_asignatura is not None:
        query_params['id-asignatura'] = id_asignatura
    if rut_alumno is not None:
        query_params['rut-alumno'] = rut_alumno

    # Concatenar parámetros de consulta si hay alguno
    if query_params:
        url_with_query = f"{url}?{urlencode(query_params)}"
    else:
        url_with_query = url

    return url_with_query

# Vistas que retornan JSON (abria que implementar una api pero meh...)
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

def obtener_usuario(request):
    nombre_usuario = request.GET.get('username', '')
    try:
        usuario = Usuario.objects.get(username=nombre_usuario)
        
        # Verificar pertenencia a grupos
        grupo_alumnos = Group.objects.get(name='Alumnos')
        grupo_profesores = Group.objects.get(name='Profesores')
        grupo_apoderados = Group.objects.get(name='Apoderados')
        
        usuario_data = {
            'username': usuario.username,
            'email': usuario.email,
            'tutor': usuario.tutor.username if usuario.tutor else None,
            'is_alumno': usuario.groups.filter(name='Alumnos').exists(),
            'is_profesor': usuario.groups.filter(name='Profesores').exists(),
            'is_apoderado': usuario.groups.filter(name='Apoderados').exists(),
        }
    except Usuario.DoesNotExist:
        usuario_data = {'error': 'Usuario no encontrado'}
    
    return JsonResponse(usuario_data, safe=False)

# Views...

def index(request):
    if request.user.is_authenticated:
        return redirect('home')
     
    data = {}
    data["titulo_pagina"] = "Inicio - Aula virtual"
    
    if request.method == 'POST':
        username = request.POST['input-username-index']
        password = request.POST['input-password-index']
        recordarme = request.POST.get('check-recordarme-index') == 'on'

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not recordarme:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(None)  # Usa la duración predeterminada de la sesión
            return redirect('home')
        else:
            data["usuario_invalido"] = "Usuario y/o contraseña incorrectos"


    return render(request, "aula_virtual/index.html", data)

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def home(request):
    data = {}
    usuario = request.user
    data['usuario'] = usuario


    # Usuario es administrador.
    if usuario.is_superuser:
        data["es_administrador"] = True
    

    # Usuario es Apoderado
    if usuario.groups.filter(name="Apoderados").exists():
        data["es_apoderado"] = True
        alumnos = list(Usuario.objects.all().filter(tutor = usuario))
        data['mis_alumnos'] = []
        for alumno in alumnos:
            asistencias = Asistencia.objects.all().filter(alumno = alumno)
            ausencias = asistencias.filter(estado='A')
            asistencias_justificadas = AsistenciaJustificacion.objects.values_list('ID_asistencia', flat=True)
            ausencias_no_justificadas = list(ausencias.exclude(id__in=asistencias_justificadas))
            retrasos = asistencias.filter(estado='R')
            retrasos_no_justificados = list(retrasos.exclude(id__in=asistencias_justificadas))
        
            new_alumno = {
                "nombre": f'{alumno.first_name} {alumno.last_name}',
                "username": alumno.username,
                "total_asistencias": len(list(asistencias)),
                "total_presente": len(list(asistencias.filter(estado = "P"))),
                "total_ausente": len(list(ausencias)),
                "total_retraso": len(list(retrasos)),
                "total_sin_registrar": len(list(asistencias.filter(estado = "S"))),
                "ausencia_no_justificada": len(ausencias_no_justificadas),
                "retraso_no_justificado": len(retrasos_no_justificados),
            }
            
                
            data['mis_alumnos'].append(new_alumno)
    # Usuario es Alumno
    if usuario.groups.filter(name="Alumnos").exists():
        data["es_alumno"] = True

    # Usuario es profesor
    if usuario.groups.filter(name="Profesores").exists():
        data["es_profesor"] = True
        
    
    return render(request, 'aula_virtual/home.html', data)

@login_required
def nuevo_usuario(request):
    usuario_autenticado = request.user
    if usuario_autenticado.is_superuser == False:
        return render(request, 'aula_virtual/usuario-sin-permiso.html', {})
    flag_crear_usuario = False
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

        try:
            # Intenta obtener el usuario existente
            usuario_nuevo = Usuario.objects.get(username=username)
            usuario_nuevo.email = email
            usuario_nuevo.set_password(password)  # Actualiza la contraseña si es necesario
            usuario_nuevo.is_active = is_active
            usuario_nuevo.is_staff = is_staff
            usuario_nuevo.is_superuser = is_superuser
        except Usuario.DoesNotExist:
            # Si el usuario no existe, créalo
            flag_crear_usuario = True
            usuario_nuevo = Usuario.objects.create(
                username=username,
                email=email,
                is_active=is_active,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            usuario_nuevo.set_password(password)

        # Guardar cambios en el usuario
        usuario_nuevo.save()

        # Eliminar grupos anteriores
        usuario_nuevo.groups.clear()

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

# -------------------------------------------------------------------
    if flag_crear_usuario:
        token_autenticacion = uuid.uuid4()
        dead_time = timezone.now() + timezone.timedelta(days=7); # 7 Token valido por 7 dias
        nuevo_token = Token.objects.create(
            token_autenticacion = token_autenticacion,
            dead_time = dead_time,
            ID_usuario = usuario_nuevo,
        )

        nuevo_token.save();
    
        subject = 'Termina de configurar tu cuenta en Aula virutal TechZenith'
        message = f'Por favor, haz clic en el siguiente enlace para terminar de configurar tu cuenta: http://127.0.0.1:8000/configuracion-cuenta/{nuevo_token.token_autenticacion}/'
        from_email = 'saad11012002@gmail.com'
        recipient_list = [usuario_nuevo.email]
        send_mail(subject, message, from_email, recipient_list)
    
    return render(request, 'aula_virtual/new-user.html', {})

def configuracion_cuenta(request, token):
    try:
        token_obj = Token.objects.get(token_autenticacion = token)
        
        # Verificar si el token ha expirado
        if token_obj.is_expired():
            return render(request, 'aula_virtual/configurar-cuenta.html', {
                "expiro": True
            })
        
        usuario = token_obj.ID_usuario
        data = {"ok": True}
        
    except Token.DoesNotExist:
        return render(request, 'aula_virtual/configurar-cuenta.html', {
            "no_existe": True
        })

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first-name', '')
        usuario.last_name = request.POST.get('last-name', '')
        usuario.set_password(request.POST.get('password', ''))
        usuario.is_active = True
        usuario.save()
        token_obj.delete()
        data['ok'] = False
        data['exito'] = True

    return render(request, 'aula_virtual/configurar-cuenta.html', data)

@login_required
def mis_asignaturas(request):
    usuario = request.user
    registros = RegistroAsignatura.objects.filter(usuario = usuario)
    asignaturas = [registro.asignatura for registro in registros]
    return render(request, 'aula_virtual/asignaturas.html',{'asignaturas': asignaturas})

from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from .models import Asistencia, Justificacion, AsistenciaJustificacion

@login_required
def justificar(request, rut_alumno):
    usuario = request.user
    try:
        alumno = Usuario.objects.get(username=rut_alumno)
    except Usuario.DoesNotExist:
        return HttpResponseBadRequest("El rut no es válido")
    
    if alumno.tutor != usuario:
        return render(request, 'aula_virtual/usuario-sin-permiso.html', {})

    asistencias = Asistencia.objects.filter(alumno=alumno)
    asistencias_justificadas = AsistenciaJustificacion.objects.values_list('ID_asistencia', flat=True)
    ausencias_no_justificadas = asistencias.filter(estado='A').exclude(id__in=asistencias_justificadas)
    retrasos_no_justificados = asistencias.filter(estado='R').exclude(id__in=asistencias_justificadas)

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        certificado = request.FILES.get('certificado')
        asistencia_ids = request.POST.getlist('asistencia_ids')

        for asistencia_id in asistencia_ids:
            try:
                asistencia = Asistencia.objects.get(pk=asistencia_id, alumno=alumno)
                justificacion = Justificacion.objects.create(
                    ID_apoderado=usuario,
                    mensaje=mensaje,
                    certificado=certificado,
                    fecha_justificacion=asistencia.dia
                )
                AsistenciaJustificacion.objects.create(ID_asistencia=asistencia, ID_justificacion=justificacion)
            except Asistencia.DoesNotExist:
                pass  # Maneja el caso donde la asistencia no exista o no pertenezca al alumno correctamente

        return redirect('home')  # Redirige a donde necesites después de justificar

    data = {
        'ausencias_no_justificadas': ausencias_no_justificadas,
        'retrasos_no_justificados': retrasos_no_justificados,
        'alumno': alumno
    }

    return render(request, 'aula_virtual/justificar.html', data)
