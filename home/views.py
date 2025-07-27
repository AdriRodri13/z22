from django.shortcuts import render, get_object_or_404
from .models import *

def home(request):
    temporada = Temporada.objects.prefetch_related('ligas__equipos').latest()
    ligas = temporada.ligas.all()

    context = {
        'temporada': temporada,
        'ligas': ligas,
    }
    return render(request, 'home/home.html', context)

def liga_detail(request, liga_id):
    liga = get_object_or_404(Liga, id=liga_id)
    equipos = liga.equipos.all().order_by('nombre')
    
    # Búsqueda si hay query
    search_query = request.GET.get('search', '')
    if search_query:
        equipos = equipos.filter(nombre__icontains=search_query)
    
    context = {
        'liga': liga,
        'equipos': equipos,
        'search_query': search_query,
        'total_equipos': liga.equipos.count(),
    }
    return render(request, 'home/liga.html', context)

def equipo_detail(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    equipaciones = equipo.equipaciones.filter(temporada=equipo.liga.temporada).order_by('id')
    
    context = {
        'equipo': equipo,
        'liga': equipo.liga,
        'equipaciones': equipaciones,
        'total_equipaciones': equipaciones.count(),
    }
    return render(request, 'home/equipo.html', context)