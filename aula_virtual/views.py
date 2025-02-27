from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Usuario, RegistroAsignatura, Asignatura, Token,Calificacion, Asistencia, AsistenciaJustificacion, Material, Justificacion, Evaluacion, RegistroAsignatura
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseBadRequest, Http404, FileResponse
from django.core.exceptions import PermissionDenied
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
from .utils import enviar_notificacion_a_alumnos
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.contrib.auth.views import PasswordResetView
from .forms import CustomPasswordResetForm

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        associated_users = Usuario.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                subject = _("Solicitud de restablecimiento de contraseña")
                email_template_name = "registration/password_reset_email.html"
                c = {
                    "email": user.email,
                    "domain": request.META['HTTP_HOST'],
                    "site_name": "TechZenith",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    "protocol": "http",
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, 'admin@techzenith.com', [user.email], fail_silently=False)
                except Exception as e:
                    messages.error(request, f"Error enviando el correo: {e}")
                messages.success(request, _("Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña."))
                return redirect("/")
        else:
            messages.error(request, _("No se encontró una cuenta con esa dirección de correo electrónico."))
    return render(request, "registration/password_reset_form.html")

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
            enviar_notificacion_a_alumnos(form)
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
    #if usuario.is_superuser:
        data["es_alumno"] = True
        # Obtener todas las asignaturas en las que el alumno está inscrito
        asignaturas_usuario = RegistroAsignatura.objects.filter(usuario=usuario).values_list('asignatura', flat=True)

        # Obtener los objetos de asignatura a partir de las IDs obtenidas
        asignaturas = Asignatura.objects.filter(id__in=asignaturas_usuario)

        # Obtener los anuncios que corresponden a estas asignaturas
        anuncios = Anuncio.objects.filter(asignatura__in=asignaturas)

        data['asignaturas'] = asignaturas
        data['anuncios'] = anuncios
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


@login_required
def material_asignatura(request, id):
    asignatura = get_object_or_404(Asignatura, id=id)
    materiales = Material.objects.filter(asignatura_id=asignatura)

    es_profesor = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='PROFESOR').exists()
    es_alumno = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='ALUMNO').exists()

    if not es_profesor and not es_alumno:
        return render(request,'aula_virtual/usuario-sin-permiso.html')


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
        return render(request,'aula_virtual/usuario-sin-permiso.html')

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
        return render(request,'aula_virtual/usuario-sin-permiso.html')

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
        return render(request,'aula_virtual/usuario-sin-permiso.html')

    if request.method == 'POST':
        material.delete()
        return redirect('material_asignatura', id=material.asignatura.id)
    return render(request, 'aula_virtual/borrar_material.html', {'material': material})

@login_required
def descargar_material(request, id):
    material = get_object_or_404(Material, id=id)
    
    # Verifica que el usuario esté registrado en la asignatura
    if not RegistroAsignatura.objects.filter(usuario=request.user, asignatura_id=material.asignatura).exists():
        raise Http404("No está autorizado para acceder a este material")
    
    return FileResponse(material.archivo, as_attachment=True, filename=material.archivo.name)

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


@login_required
def calificaciones_asignatura(request, asignatura_id):
    usuario = request.user
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    calificaciones = Calificacion.objects.filter(ID_usuario=usuario, ID_evaluacion__asignatura=asignatura)
    evaluaciones = Evaluacion.objects.filter(asignatura=asignatura)
    estudiantes = RegistroAsignatura.objects.filter(asignatura_id=asignatura, rol='ALUMNO').select_related('usuario')

    es_profesor = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='PROFESOR').exists()
    es_alumno = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='ALUMNO').exists()

    if not es_profesor and not es_alumno:
        return render(request,'aula_virtual/usuario-sin-permiso.html')



    return render(request, 'aula_virtual/calificaciones_asignatura.html', {
        'asignatura': asignatura,
        'calificaciones': calificaciones,
        'es_profesor': es_profesor,
        'es_alumno': es_alumno,
        'evaluaciones': evaluaciones,
        'estudiantes': [e.usuario for e in estudiantes],
        
    })


@login_required
def agregar_calificacion(request, evaluacion_id):
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    asignatura = evaluacion.asignatura
    es_profesor = RegistroAsignatura.objects.filter(asignatura_id=asignatura, usuario=request.user, rol='PROFESOR').exists()

    if not es_profesor:
        return render(request,'aula_virtual/usuario-sin-permiso.html')



    if request.method == 'POST':
        for usuario_id in request.POST.getlist('usuario_id'):
            comentario = request.POST.get(f'comentario_{usuario_id}')
            calificacion = request.POST.get(f'calificacion_{usuario_id}')
            if calificacion:
                usuario = get_object_or_404(Usuario, id=usuario_id)
                Calificacion.objects.update_or_create(
                    ID_usuario=usuario,
                    ID_evaluacion=evaluacion,
                    defaults={'comentario': comentario, 'calificacion': calificacion}
                )
        return redirect('calificaciones_asignatura', asignatura_id=asignatura.id)

    estudiantes = RegistroAsignatura.objects.filter(asignatura_id=asignatura, rol='ALUMNO').select_related('usuario')
    calificaciones = Calificacion.objects.filter(ID_evaluacion=evaluacion)
    estudiantes_calificaciones = []

    for estudiante in estudiantes:
        calificacion = calificaciones.filter(ID_usuario=estudiante.usuario).first()
        estudiantes_calificaciones.append({
            'estudiante': estudiante.usuario,
            'calificacion': calificacion
        })

    return render(request, 'aula_virtual/agregar_calificacion.html', {
        'evaluacion': evaluacion,
        'asignatura': asignatura,
        'estudiantes_calificaciones':estudiantes_calificaciones
    })


@login_required
def agregar_evaluacion(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    es_profesor = RegistroAsignatura.objects.filter(asignatura=asignatura, usuario=request.user, rol='PROFESOR').exists()

    if not es_profesor:
        return render(request,'aula_virtual/usuario-sin-permiso.html')

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_termino = request.POST.get('fecha_termino')
        tipo = request.POST.get('tipo')

        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_termino = datetime.strptime(fecha_termino, '%Y-%m-%d')
        evaluacion = Evaluacion(
            asignatura=asignatura,
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino,
            tipo=tipo

        )
        evaluacion.save()
        return redirect('agregar_evaluacion', asignatura_id=asignatura.id)

    return render(request, 'aula_virtual/agregar_evaluacion.html', {'asignatura': asignatura})