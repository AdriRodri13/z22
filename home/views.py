from django.shortcuts import render, get_object_or_404
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