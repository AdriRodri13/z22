from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import json
from .models import *

def home(request):
    # Obtener todas las secciones con sus subsecciones
    secciones = Seccion.objects.prefetch_related(
        'subsecciones__subsubsecciones'
    ).order_by('nombre')

    context = {
        'secciones': secciones,
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
        nombre_cliente = data.get('nombre', '').strip()
        instagram_cliente = data.get('instagram', '').strip()
        productos_cesta = data.get('productos', [])

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

        # Preparar datos para el email
        total = 0
        productos_detalle = []

        for producto in productos_cesta:
            try:
                prenda = Prenda.objects.get(id=producto['id'])
                precio_num = float(producto['precio'].replace('€', '').replace(',', '.').strip())
                total += precio_num

                productos_detalle.append({
                    'nombre': prenda.nombre,
                    'precio': producto['precio'],
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
            'cantidad_productos': len(productos_detalle)
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