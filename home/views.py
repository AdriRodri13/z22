from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
from django.db import models
import json
from .models import *
from .forms import RegistroForm

def home(request):
    # Obtener todas las secciones con sus subsecciones
    secciones = Seccion.objects.prefetch_related(
        'subsecciones__subsubsecciones'
    ).order_by('nombre')

    # Lógica para mostrar el alert de registro a usuarios nuevos
    mostrar_alert_registro = False
    if not request.user.is_authenticated:
        # Verificar si es la primera visita (no ha rechazado el registro)
        if not request.session.get('registro_rechazado', False):
            mostrar_alert_registro = True

    context = {
        'secciones': secciones,
        'mostrar_alert_registro': mostrar_alert_registro,
    }
    return render(request, 'home/home.html', context)

def seccion_detail(request, seccion_id):
    seccion = get_object_or_404(Seccion, id=seccion_id)
    subsecciones = seccion.subsecciones.all().order_by('nombre')
    
    # Búsqueda si hay query
    search_query = request.GET.get('search', '')
    if search_query:
        subsecciones = subsecciones.filter(nombre__icontains=search_query)
    
    context = {
        'seccion': seccion,
        'subsecciones': subsecciones,
        'search_query': search_query,
        'total_subsecciones': seccion.subsecciones.count(),
    }
    return render(request, 'home/seccion.html', context)

def subseccion_detail(request, subseccion_id):
    subseccion = get_object_or_404(Subseccion, id=subseccion_id)
    subsubsecciones = subseccion.subsubsecciones.all().order_by('nombre')
    
    # Búsqueda si hay query
    search_query = request.GET.get('search', '')
    if search_query:
        subsubsecciones = subsubsecciones.filter(nombre__icontains=search_query)
    
    context = {
        'subseccion': subseccion,
        'seccion': subseccion.seccion,
        'subsubsecciones': subsubsecciones,
        'search_query': search_query,
        'total_subsubsecciones': subseccion.subsubsecciones.count(),
    }
    return render(request, 'home/subseccion.html', context)

def subsubseccion_detail(request, subsubseccion_id):
    subsubseccion = get_object_or_404(Subsubseccion, id=subsubseccion_id)
    prendas = subsubseccion.prendas.all().order_by('-creado_en')
    
    # Filtros adicionales
    search_query = request.GET.get('search', '')
    if search_query:
        prendas = prendas.filter(
            nombre__icontains=search_query
        )
    
    context = {
        'subsubseccion': subsubseccion,
        'subseccion': subsubseccion.subseccion,
        'seccion': subsubseccion.subseccion.seccion,
        'prendas': prendas,
        'search_query': search_query,
        'total_prendas': subsubseccion.prendas.count(),
    }
    return render(request, 'home/subsubseccion.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def consultar_disponibilidad(request):
    try:
        # Parsear datos del request
        data = json.loads(request.body)
        usuario_autenticado = data.get('usuario_autenticado', False)
        productos_cesta = data.get('productos', [])

        # Si es usuario autenticado, obtener datos del usuario
        if usuario_autenticado and request.user.is_authenticated:
            if hasattr(request.user, 'profile'):
                nombre_cliente = f"{request.user.first_name} {request.user.last_name}".strip()
                if not nombre_cliente:
                    # Si no tiene nombre completo, usar el username
                    nombre_cliente = request.user.username
                instagram_cliente = request.user.profile.instagram_account
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Usuario no tiene perfil configurado'
                }, status=400)
        else:
            # Usuario no autenticado - obtener datos del formulario
            nombre_cliente = data.get('nombre', '').strip()
            instagram_cliente = data.get('instagram', '').strip()

        # Validar datos
        if not nombre_cliente or not instagram_cliente:
            return JsonResponse({
                'success': False,
                'error': 'Nombre e Instagram son requeridos'
            }, status=400)

        if not productos_cesta:
            return JsonResponse({
                'success': False,
                'error': 'La cesta está vacía'
            }, status=400)

        # Buscar usuario por Instagram para verificar descuentos
        usuario_descuento = None
        codigo_vigente = None
        try:
            usuario_descuento = User.objects.select_related('profile').get(
                profile__instagram_account=instagram_cliente
            )
            # Buscar código vigente activo
            from django.utils import timezone
            codigo_vigente = CodigoDescuento.objects.filter(
                user=usuario_descuento,
                usado=False,
                fecha_expiracion__gt=timezone.now()
            ).order_by('-fecha_creacion').first()
        except User.DoesNotExist:
            pass

        # Preparar datos para el email
        total = 0
        total_con_descuento = 0
        productos_detalle = []

        for producto in productos_cesta:
            try:
                prenda = Prenda.objects.get(id=producto['id'])
                precio_num = float(producto['precio'].replace('€', '').replace(',', '.').strip())
                total += precio_num

                # Calcular precio con descuento si aplica
                precio_con_descuento = precio_num
                if codigo_vigente:
                    precio_con_descuento = precio_num * (1 - codigo_vigente.porcentaje / 100)
                    total_con_descuento += precio_con_descuento

                productos_detalle.append({
                    'nombre': prenda.nombre,
                    'precio': producto['precio'],
                    'precio_con_descuento': f"{precio_con_descuento:.2f}€" if codigo_vigente else None,
                    'imagen_url': prenda.imagen.url if prenda.imagen else '',
                    'subsubseccion': prenda.subsubseccion.nombre,
                    'subseccion': prenda.subsubseccion.subseccion.nombre,
                    'seccion': prenda.subsubseccion.subseccion.seccion.nombre
                })
            except (Prenda.DoesNotExist, ValueError):
                continue

        # Crear contexto para el template del email
        context = {
            'nombre_cliente': nombre_cliente,
            'instagram_cliente': instagram_cliente,
            'productos': productos_detalle,
            'total': f"{total:.2f}€",
            'total_con_descuento': f"{total_con_descuento:.2f}€" if codigo_vigente else None,
            'cantidad_productos': len(productos_detalle),
            'codigo_descuento': codigo_vigente,
            'porcentaje_descuento': codigo_vigente.porcentaje if codigo_vigente else None,
            'ahorro_total': f"{(total - total_con_descuento):.2f}€" if codigo_vigente else None
        }

        # Renderizar email HTML
        html_message = render_to_string('emails/consulta_disponibilidad.html', context)
        plain_message = strip_tags(html_message)

        # Enviar email
        subject = f'Consulta de Disponibilidad - {nombre_cliente} (@{instagram_cliente})'

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['zoonnee22@gmail.com'],
            fail_silently=False,
        )

        return JsonResponse({
            'success': True,
            'message': 'Consulta enviada correctamente. Te contactaremos pronto por Instagram.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido @{user.profile.instagram_account}! Tu cuenta ha sido creada exitosamente.')
            return redirect('home:perfil_usuario')
    else:
        form = RegistroForm()

    return render(request, 'home/registro.html', {'form': form})


@csrf_exempt
@require_http_methods(["POST"])
def rechazar_registro(request):
    # Marcar en la sesión que el usuario rechazó el registro
    request.session['registro_rechazado'] = True
    return JsonResponse({'success': True})


@login_required
def perfil_usuario(request):
    return render(request, 'home/perfil_usuario.html')


@csrf_exempt
@require_http_methods(["POST"])
def agregar_carrito(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        prenda_id = data.get('prenda_id')

        if not prenda_id:
            return JsonResponse({'success': False, 'error': 'ID de prenda requerido'}, status=400)

        # Obtener la prenda
        try:
            prenda = Prenda.objects.get(id=prenda_id)
        except Prenda.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Prenda no encontrada'}, status=404)

        # Crear o actualizar item del carrito
        carrito_item, created = CarritoItem.objects.get_or_create(
            user=request.user,
            prenda=prenda
        )

        # Si ya existía, actualizar última actividad
        if not created:
            carrito_item.save()  # Esto actualiza ultima_actividad automáticamente

        return JsonResponse({
            'success': True,
            'created': created,
            'message': 'Agregado al carrito' if created else 'Ya estaba en el carrito'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Error interno'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def remover_carrito(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        prenda_id = data.get('prenda_id')

        if not prenda_id:
            return JsonResponse({'success': False, 'error': 'ID de prenda requerido'}, status=400)

        # Buscar y eliminar el item del carrito
        try:
            carrito_item = CarritoItem.objects.get(user=request.user, prenda_id=prenda_id)
            carrito_item.delete()

            return JsonResponse({
                'success': True,
                'message': 'Eliminado del carrito'
            })
        except CarritoItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item no encontrado en el carrito'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Error interno'}, status=500)


@login_required
def obtener_carrito(request):
    try:
        carrito_items = CarritoItem.objects.filter(user=request.user).select_related('prenda')

        items_data = []
        for item in carrito_items:
            items_data.append({
                'id': item.prenda.id,
                'nombre': item.prenda.nombre or f"Prenda de {item.prenda.subsubseccion.nombre}",
                'precio': f"{item.prenda.precio}€" if item.prenda.precio else "Precio no disponible",
                'imagen': item.prenda.imagen.url if item.prenda.imagen else '',
                'agregado_en': item.agregado_en.isoformat(),
                'ultima_actividad': item.ultima_actividad.isoformat()
            })

        return JsonResponse({
            'success': True,
            'items': items_data,
            'count': len(items_data)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Error al obtener carrito'}, status=500)


@login_required
def obtener_descuentos_usuario(request):
    """
    Obtener códigos de descuento vigentes del usuario para mostrar en la cesta
    """
    try:
        from django.utils import timezone

        # Buscar códigos activos (no usados y no expirados)
        codigos_activos = CodigoDescuento.objects.filter(
            user=request.user,
            usado=False
        ).filter(
            # Sin fecha de expiración O con fecha futura
            models.Q(fecha_expiracion__isnull=True) |
            models.Q(fecha_expiracion__gt=timezone.now())
        ).order_by('-fecha_creacion')

        descuentos_data = []
        for codigo in codigos_activos:
            descuentos_data.append({
                'codigo': codigo.codigo,
                'porcentaje': codigo.porcentaje,
                'fecha_expiracion': codigo.fecha_expiracion.isoformat() if codigo.fecha_expiracion else None,
                'fecha_creacion': codigo.fecha_creacion.isoformat()
            })

        return JsonResponse({
            'success': True,
            'descuentos': descuentos_data,
            'count': len(descuentos_data)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Error al obtener descuentos'}, status=500)


def login_usuario(request):
    """
    Vista de login específica para usuarios clientes (no administradores)
    """
    from django.contrib.auth import authenticate, login as django_login

    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, 'Por favor completa todos los campos')
            return render(request, 'home/login_usuario.html')

        # Intentar autenticar
        user = authenticate(request, username=email, password=password)

        if user is not None:
            django_login(request, user)
            messages.success(request, f'¡Bienvenido de vuelta!')

            # Redirigir según el tipo de usuario
            if hasattr(user, 'profile') and user.profile:
                # Usuario cliente normal
                return redirect('home:perfil_usuario')
            elif user.is_staff:
                # Administrador logueado desde interfaz de cliente
                return redirect('panel_admin:dashboard')
            else:
                # Usuario sin perfil
                return redirect('home:home')
        else:
            messages.error(request, 'Email o contraseña incorrectos')

    return render(request, 'home/login_usuario.html')