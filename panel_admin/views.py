from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.urls import reverse_lazy
from home.models import Temporada, Liga, Equipo, Equipacion
from .forms import TemporadaForm, LigaForm, EquipoForm, EquipacionForm
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


class AdminLoginView(LoginView):
    template_name = 'panel_admin/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('panel_admin:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Acceso Panel de Administración'
        return context
    
    def form_valid(self, form):
        # Verificar que el usuario es staff
        user = form.get_user()
        if not user.is_staff:
            messages.error(self.request, 'No tienes permisos para acceder al panel de administración.')
            return self.form_invalid(form)
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class AdminLogoutView(LogoutView):
    """Vista de logout específica para el panel de administración"""
    template_name = 'panel_admin/logout.html'
    next_page = reverse_lazy('panel_admin:login')  # Redirige al login del panel admin
    http_method_names = ['get', 'post']  # Permitir tanto GET como POST
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cerrar Sesión - Panel de Administración'
        return context
    
    def get(self, request, *args, **kwargs):
        """Manejar GET request - mostrar página de confirmación"""
        return super().get(request, *args, **kwargs)

@login_required
@user_passes_test(is_staff_user)
def dashboard(request):
    # Estadísticas generales
    stats = {
        'total_temporadas': Temporada.objects.count(),
        'total_ligas': Liga.objects.count(),
        'total_equipos': Equipo.objects.count(),
        'total_equipaciones': Equipacion.objects.count(),
    }
    
    # Últimas incorporaciones
    ultimas_temporadas = Temporada.objects.order_by('-creado_en')[:5]
    ultimas_ligas = Liga.objects.order_by('-id')[:5]
    ultimos_equipos = Equipo.objects.order_by('-id')[:5]
    ultimas_equipaciones = Equipacion.objects.order_by('-id')[:5]
    
    context = {
        'title': 'Panel de Administración',
        'stats': stats,
        'ultimas_temporadas': ultimas_temporadas,
        'ultimas_ligas': ultimas_ligas,
        'ultimos_equipos': ultimos_equipos,
        'ultimas_equipaciones': ultimas_equipaciones,
    }
    return render(request, 'panel_admin/dashboard.html', context)


# =================== TEMPORADAS ===================
@login_required
@user_passes_test(is_staff_user)
def temporada_list(request):
    temporadas = Temporada.objects.annotate(
        total_ligas=Count('ligas', distinct=True),
        total_equipaciones=Count('ligas__equipos__equipaciones', 
                               filter=Q(ligas__equipos__equipaciones__temporada_id=F('id')), 
                               distinct=True)
    ).order_by('-creado_en')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        temporadas = temporadas.filter(nombre__icontains=search)
    
    # Paginación
    paginator = Paginator(temporadas, 10)
    page = request.GET.get('page')
    temporadas = paginator.get_page(page)
    
    context = {
        'title': 'Gestión de Temporadas',
        'temporadas': temporadas,
        'search': search,
    }
    return render(request, 'panel_admin/temporada/temporada_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def temporada_create(request):
    if request.method == 'POST':
        form = TemporadaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Temporada creada exitosamente.')
            return redirect('panel_admin:temporada_list')
    else:
        form = TemporadaForm()
    
    context = {
        'title': 'Crear Temporada',
        'form': form,
        'action': 'crear'
    }
    return render(request, 'panel_admin/temporada/temporada_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def temporada_edit(request, pk):
    temporada = get_object_or_404(Temporada, pk=pk)
    
    if request.method == 'POST':
        form = TemporadaForm(request.POST, instance=temporada)
        if form.is_valid():
            form.save()
            messages.success(request, 'Temporada actualizada exitosamente.')
            return redirect('panel_admin:temporada_list')
    else:
        form = TemporadaForm(instance=temporada)
    
    context = {
        'title': 'Editar Temporada',
        'form': form,
        'temporada': temporada,
        'action': 'editar'
    }
    return render(request, 'panel_admin/temporada/temporada_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def temporada_delete(request, pk):
    temporada = get_object_or_404(Temporada, pk=pk)
    
    if request.method == 'POST':
        temporada.delete()
        messages.success(request, 'Temporada eliminada exitosamente.')
        return redirect('panel_admin:temporada_list')
    
    context = {
        'title': 'Eliminar Temporada',
        'temporada': temporada,
    }
    return render(request, 'panel_admin/temporada/temporada_delete.html', context)


# =================== LIGAS ===================
@login_required
@user_passes_test(is_staff_user)
def liga_list(request):
    ligas = Liga.objects.select_related('temporada').annotate(
        total_equipos=Count('equipos')
    ).order_by('temporada__nombre', 'nombre')
    
    # Filtros
    search = request.GET.get('search', '')
    temporada_id = request.GET.get('temporada', '')
    
    if search:
        ligas = ligas.filter(
            Q(nombre__icontains=search) |
            Q(temporada__nombre__icontains=search)
        )
    
    if temporada_id:
        ligas = ligas.filter(temporada_id=temporada_id)
    
    # Paginación
    paginator = Paginator(ligas, 10)
    page = request.GET.get('page')
    ligas = paginator.get_page(page)
    
    temporadas = Temporada.objects.order_by('-creado_en')
    
    context = {
        'title': 'Gestión de Ligas',
        'ligas': ligas,
        'temporadas': temporadas,
        'search': search,
        'selected_temporada': temporada_id,
    }
    return render(request, 'panel_admin/liga/liga_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def liga_create(request):
    if request.method == 'POST':
        form = LigaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Liga creada exitosamente.')
            return redirect('panel_admin:liga_list')
    else:
        form = LigaForm()
    
    context = {
        'title': 'Crear Liga',
        'form': form,
        'action': 'crear'
    }
    return render(request, 'panel_admin/liga/liga_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def liga_edit(request, pk):
    liga = get_object_or_404(Liga, pk=pk)
    
    if request.method == 'POST':
        form = LigaForm(request.POST, request.FILES, instance=liga)
        if form.is_valid():
            form.save()
            messages.success(request, 'Liga actualizada exitosamente.')
            return redirect('panel_admin:liga_list')
    else:
        form = LigaForm(instance=liga)
    
    context = {
        'title': 'Editar Liga',
        'form': form,
        'liga': liga,
        'action': 'editar'
    }
    return render(request, 'panel_admin/liga/liga_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def liga_delete(request, pk):
    liga = get_object_or_404(Liga, pk=pk)
    
    if request.method == 'POST':
        liga.delete()
        messages.success(request, 'Liga eliminada exitosamente.')
        return redirect('panel_admin:liga_list')
    
    context = {
        'title': 'Eliminar Liga',
        'liga': liga,
    }
    return render(request, 'panel_admin/liga/liga_delete.html', context)


# =================== EQUIPOS ===================
@login_required
@user_passes_test(is_staff_user)
def equipo_list(request):
    equipos = Equipo.objects.select_related('liga', 'liga__temporada').annotate(
        total_equipaciones=Count('equipaciones')
    ).order_by('liga__temporada__nombre', 'liga__nombre', 'nombre')
    
    # Filtros
    search = request.GET.get('search', '')
    liga_id = request.GET.get('liga', '')
    temporada_id = request.GET.get('temporada', '')
    
    if search:
        equipos = equipos.filter(
            Q(nombre__icontains=search) |
            Q(liga__nombre__icontains=search)
        )
    
    if liga_id:
        equipos = equipos.filter(liga_id=liga_id)
    elif temporada_id:
        equipos = equipos.filter(liga__temporada_id=temporada_id)
    
    # Paginación
    paginator = Paginator(equipos, 15)
    page = request.GET.get('page')
    equipos = paginator.get_page(page)
    
    temporadas = Temporada.objects.order_by('-creado_en')
    ligas = Liga.objects.select_related('temporada').order_by('temporada__nombre', 'nombre')
    
    context = {
        'title': 'Gestión de Equipos',
        'equipos': equipos,
        'temporadas': temporadas,
        'ligas': ligas,
        'search': search,
        'selected_liga': liga_id,
        'selected_temporada': temporada_id,
    }
    return render(request, 'panel_admin/equipo/equipo_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipo_create(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo creado exitosamente.')
            return redirect('panel_admin:equipo_list')
    else:
        form = EquipoForm()
    
    context = {
        'title': 'Crear Equipo',
        'form': form,
        'action': 'crear'
    }
    return render(request, 'panel_admin/equipo/equipo_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipo_edit(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado exitosamente.')
            return redirect('panel_admin:equipo_list')
    else:
        form = EquipoForm(instance=equipo)
    
    context = {
        'title': 'Editar Equipo',
        'form': form,
        'equipo': equipo,
        'action': 'editar'
    }
    return render(request, 'panel_admin/equipo/equipo_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipo_delete(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo eliminado exitosamente.')
        return redirect('panel_admin:equipo_list')
    
    context = {
        'title': 'Eliminar Equipo',
        'equipo': equipo,
    }
    return render(request, 'panel_admin/equipo/equipo_delete.html', context)

# =================== EQUIPOS - VISTA POR LIGAS ===================
@login_required
@user_passes_test(is_staff_user)
def equipo_list_by_liga(request):
    # Obtener la última temporada
    ultima_temporada = Temporada.objects.order_by('-creado_en').first()
    
    if not ultima_temporada:
        context = {
            'title': 'Gestión de Equipos por Liga',
            'ligas': [],
            'temporada_actual': None,
        }
        return render(request, 'panel_admin/equipo/equipo_by_liga.html', context)
    
    # Obtener ligas de la última temporada con sus equipos
    ligas = Liga.objects.filter(temporada=ultima_temporada).prefetch_related(
        'equipos'
    ).annotate(
        total_equipos=Count('equipos')
    ).order_by('nombre')
    
    context = {
        'title': 'Gestión de Equipos por Liga',
        'ligas': ligas,
        'temporada_actual': ultima_temporada,
    }
    return render(request, 'panel_admin/equipo/equipo_by_liga.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipo_list_in_liga(request, liga_id):
    liga = get_object_or_404(Liga, pk=liga_id)
    
    # Obtener equipos de esta liga
    equipos = Equipo.objects.filter(liga=liga).annotate(
        total_equipaciones=Count('equipaciones')
    ).order_by('nombre')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        equipos = equipos.filter(nombre__icontains=search)
    
    # Paginación
    paginator = Paginator(equipos, 15)
    page = request.GET.get('page')
    equipos = paginator.get_page(page)
    
    context = {
        'title': f'Equipos de {liga.nombre}',
        'liga': liga,
        'equipos': equipos,
        'search': search,
    }
    return render(request, 'panel_admin/equipo/equipo_list_in_liga.html', context)


# =================== EQUIPACIONES ===================

@login_required
@user_passes_test(is_staff_user)
def equipacion_create(request):
    # Obtener equipo preseleccionado si viene desde navegación jerárquica
    equipo_id = request.GET.get('equipo')
    initial_data = {}
    
    if equipo_id:
        try:
            equipo = Equipo.objects.get(pk=equipo_id)
            initial_data['equipo'] = equipo
            # También podemos preseleccionar la temporada de la liga del equipo
            initial_data['temporada'] = equipo.liga.temporada
        except Equipo.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = EquipacionForm(request.POST, request.FILES)
        if form.is_valid():
            equipacion = form.save()
            messages.success(request, 'Equipación creada exitosamente.')
            
            # Redirigir siempre al equipo de la equipación creada
            return redirect('panel_admin:equipacion_list_in_equipo', equipacion.equipo.id)
    else:
        form = EquipacionForm(initial=initial_data)
    
    context = {
        'title': 'Crear Equipación',
        'form': form,
        'action': 'crear',
        'equipo_preseleccionado': equipo_id
    }
    return render(request, 'panel_admin/equipacion/equipacion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipacion_edit(request, pk):
    equipacion = get_object_or_404(Equipacion, pk=pk)
    
    if request.method == 'POST':
        form = EquipacionForm(request.POST, request.FILES, instance=equipacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipación actualizada exitosamente.')
            # Redirigir al equipo de la equipación editada
            return redirect('panel_admin:equipacion_list_in_equipo', equipacion.equipo.id)
    else:
        form = EquipacionForm(instance=equipacion)
    
    context = {
        'title': 'Editar Equipación',
        'form': form,
        'equipacion': equipacion,
        'action': 'editar'
    }
    return render(request, 'panel_admin/equipacion/equipacion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipacion_delete(request, pk):
    equipacion = get_object_or_404(Equipacion, pk=pk)
    equipo_id = equipacion.equipo.id  # Guardar el ID antes de eliminar
    
    if request.method == 'POST':
        equipacion.delete()
        messages.success(request, 'Equipación eliminada exitosamente.')
        # Redirigir al equipo de la equipación eliminada
        return redirect('panel_admin:equipacion_list_in_equipo', equipo_id)
    
    context = {
        'title': 'Eliminar Equipación',
        'equipacion': equipacion,
    }
    return render(request, 'panel_admin/equipacion/equipacion_delete.html', context)

# =================== EQUIPACIONES - VISTA JERÁRQUICA ===================
@login_required
@user_passes_test(is_staff_user)
def equipacion_list_by_liga(request):
    """Vista principal de equipaciones organizadas por liga"""
    # Obtener la última temporada
    ultima_temporada = Temporada.objects.order_by('-creado_en').first()
    
    # Permitir seleccionar temporada
    temporada_id = request.GET.get('temporada', '')
    if temporada_id:
        try:
            temporada_seleccionada = Temporada.objects.get(pk=temporada_id)
        except Temporada.DoesNotExist:
            temporada_seleccionada = ultima_temporada
    else:
        temporada_seleccionada = ultima_temporada
    
    if not temporada_seleccionada:
        context = {
            'title': 'Gestión de Equipaciones por Liga',
            'ligas': [],
            'temporada_actual': None,
            'temporadas': Temporada.objects.order_by('-creado_en'),
        }
        return render(request, 'panel_admin/equipacion/equipacion_by_liga.html', context)
    
    # Obtener ligas de la temporada seleccionada con conteo correcto
    ligas = Liga.objects.filter(temporada=temporada_seleccionada).annotate(
        total_equipos=Count('equipos', distinct=True),
        total_equipaciones=Count('equipos__equipaciones', 
                               filter=Q(equipos__equipaciones__temporada=temporada_seleccionada),
                               distinct=True)
    ).order_by('nombre')
    
    temporadas = Temporada.objects.order_by('-creado_en')
    
    context = {
        'title': 'Gestión de Equipaciones por Liga',
        'ligas': ligas,
        'temporada_actual': temporada_seleccionada,
        'temporadas': temporadas,
        'selected_temporada': str(temporada_seleccionada.id) if temporada_seleccionada else '',
    }
    return render(request, 'panel_admin/equipacion/equipacion_by_liga.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipacion_list_by_equipo(request, liga_id):
    """Vista de equipos de una liga con sus equipaciones"""
    liga = get_object_or_404(Liga, pk=liga_id)
    
    # Obtener equipos de esta liga con conteo de equipaciones
    equipos = Equipo.objects.filter(liga=liga).prefetch_related(
        'equipaciones'
    ).annotate(
        total_equipaciones=Count('equipaciones', filter=Q(equipaciones__temporada=liga.temporada))
    ).order_by('nombre')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        equipos = equipos.filter(nombre__icontains=search)
    
    # Paginación
    paginator = Paginator(equipos, 12)
    page = request.GET.get('page')
    equipos = paginator.get_page(page)
    
    context = {
        'title': f'Equipaciones de {liga.nombre}',
        'liga': liga,
        'equipos': equipos,
        'search': search,
    }
    return render(request, 'panel_admin/equipacion/equipacion_by_equipo.html', context)


@login_required
@user_passes_test(is_staff_user)
def equipacion_list_in_equipo(request, equipo_id):
    """Vista de equipaciones de un equipo específico"""
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    
    # Obtener equipaciones de este equipo
    equipaciones = Equipacion.objects.filter(equipo=equipo).select_related(
        'temporada'
    ).order_by('-temporada__creado_en')
    
    # Filtro por temporada
    temporada_id = request.GET.get('temporada', '')
    if temporada_id:
        equipaciones = equipaciones.filter(temporada_id=temporada_id)
    
    # Paginación
    paginator = Paginator(equipaciones, 12)
    page = request.GET.get('page')
    equipaciones = paginator.get_page(page)
    
    temporadas = Temporada.objects.order_by('-creado_en')
    
    context = {
        'title': f'Equipaciones de {equipo.nombre}',
        'equipo': equipo,
        'equipaciones': equipaciones,
        'temporadas': temporadas,
        'selected_temporada': temporada_id,
    }
    return render(request, 'panel_admin/equipacion/equipacion_in_equipo.html', context)