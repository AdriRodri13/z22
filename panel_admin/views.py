from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Prefetch
from django.urls import reverse_lazy
from home.models import Seccion, Subseccion, Subsubseccion, Prenda
from .forms import SeccionForm, SubseccionForm, SubsubseccionForm, PrendaForm, PrendaMultipleUploadForm
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator
from datetime import datetime
from django.http import JsonResponse


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
        'total_secciones': Seccion.objects.count(),
        'total_subsecciones': Subseccion.objects.count(),
        'total_subsubsecciones': Subsubseccion.objects.count(),
        'total_prendas': Prenda.objects.count(),
    }
    
    # Últimas incorporaciones
    ultimas_secciones = Seccion.objects.order_by('-creado_en')[:5]
    ultimas_subsecciones = Subseccion.objects.order_by('-creado_en')[:5]
    ultimas_subsubsecciones = Subsubseccion.objects.order_by('-creado_en')[:5]
    ultimas_prendas = Prenda.objects.order_by('-creado_en')[:5]
    
    context = {
        'title': 'Panel de Administración',
        'stats': stats,
        'ultimas_secciones': ultimas_secciones,
        'ultimas_subsecciones': ultimas_subsecciones,
        'ultimas_subsubsecciones': ultimas_subsubsecciones,
        'ultimas_prendas': ultimas_prendas,
    }
    return render(request, 'panel_admin/dashboard.html', context)


# =================== SECCIONES ===================
@login_required
@user_passes_test(is_staff_user)
def seccion_list(request):
    secciones = Seccion.objects.annotate(
        total_subsecciones=Count('subsecciones', distinct=True),
        total_prendas=Count('subsecciones__subsubsecciones__prendas', distinct=True)
    ).order_by('nombre')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        secciones = secciones.filter(
            Q(nombre__icontains=search) |
            Q(descripcion__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(secciones, 10)
    page = request.GET.get('page')
    secciones = paginator.get_page(page)
    
    context = {
        'title': 'Gestión de Secciones',
        'secciones': secciones,
        'search': search,
    }
    return render(request, 'panel_admin/seccion/seccion_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def seccion_create(request):
    if request.method == 'POST':
        form = SeccionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sección creada exitosamente.')
            return redirect('panel_admin:seccion_list')
    else:
        form = SeccionForm()
    
    context = {
        'title': 'Crear Sección',
        'form': form,
        'action': 'crear'
    }
    return render(request, 'panel_admin/seccion/seccion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def seccion_edit(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    
    if request.method == 'POST':
        form = SeccionForm(request.POST, request.FILES, instance=seccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sección actualizada exitosamente.')
            return redirect('panel_admin:seccion_list')
    else:
        form = SeccionForm(instance=seccion)
    
    context = {
        'title': 'Editar Sección',
        'form': form,
        'seccion': seccion,
        'action': 'editar'
    }
    return render(request, 'panel_admin/seccion/seccion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def seccion_delete(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    
    if request.method == 'POST':
        seccion.delete()
        messages.success(request, 'Sección eliminada exitosamente.')
        return redirect('panel_admin:seccion_list')
    
    context = {
        'title': 'Eliminar Sección',
        'seccion': seccion,
    }
    return render(request, 'panel_admin/seccion/seccion_delete.html', context)


# =================== SUBSECCIONES ===================
@login_required
@user_passes_test(is_staff_user)
def subseccion_list(request):
    # Obtener todas las secciones con sus subsecciones agrupadas
    secciones_con_subsecciones = Seccion.objects.prefetch_related(
        Prefetch(
            'subsecciones', 
            queryset=Subseccion.objects.annotate(
                total_subsubsecciones=Count('subsubsecciones')
            ).order_by('nombre')
        )
    ).annotate(
        total_subsecciones=Count('subsecciones', distinct=True)
    ).order_by('nombre')
    
    # Filtro de búsqueda (para JavaScript)
    search = request.GET.get('search', '')
    
    context = {
        'title': 'Gestión de Subsecciones',
        'secciones_con_subsecciones': secciones_con_subsecciones,
        'search': search,
    }
    return render(request, 'panel_admin/subseccion/subseccion_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def subseccion_create(request):
    # Obtener ID de sección desde parámetros GET
    seccion_id = request.GET.get('seccion_id')
    seccion_preseleccionada = None
    
    if seccion_id:
        try:
            seccion_preseleccionada = Seccion.objects.get(pk=seccion_id)
        except Seccion.DoesNotExist:
            seccion_preseleccionada = None
    
    if request.method == 'POST':
        form = SubseccionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subsección creada exitosamente.')
            return redirect('panel_admin:subseccion_list')
    else:
        # Preseleccionar la sección si se pasa como parámetro
        initial_data = {}
        if seccion_preseleccionada:
            initial_data['seccion'] = seccion_preseleccionada
        form = SubseccionForm(initial=initial_data)
    
    context = {
        'title': 'Crear Subsección',
        'form': form,
        'action': 'crear',
        'seccion_preseleccionada': seccion_preseleccionada
    }
    return render(request, 'panel_admin/subseccion/subseccion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def subseccion_edit(request, pk):
    subseccion = get_object_or_404(Subseccion, pk=pk)
    
    if request.method == 'POST':
        form = SubseccionForm(request.POST, request.FILES, instance=subseccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subsección actualizada exitosamente.')
            return redirect('panel_admin:subseccion_list')
    else:
        form = SubseccionForm(instance=subseccion)
    
    context = {
        'title': 'Editar Subsección',
        'form': form,
        'subseccion': subseccion,
        'action': 'editar'
    }
    return render(request, 'panel_admin/subseccion/subseccion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def subseccion_delete(request, pk):
    subseccion = get_object_or_404(Subseccion, pk=pk)
    
    if request.method == 'POST':
        subseccion.delete()
        messages.success(request, 'Subsección eliminada exitosamente.')
        return redirect('panel_admin:subseccion_list')
    
    context = {
        'title': 'Eliminar Subsección',
        'subseccion': subseccion,
    }
    return render(request, 'panel_admin/subseccion/subseccion_delete.html', context)


# =================== SUBSUBSECCIONES ===================
@login_required
@user_passes_test(is_staff_user)
def subsubseccion_list(request):
    # Obtener parámetro de subsección seleccionada
    selected_subseccion_id = request.GET.get('subseccion_id')
    
    if selected_subseccion_id:
        # PASO 2: Mostrar subsubsecciones de la subsección seleccionada
        try:
            subseccion_seleccionada = Subseccion.objects.select_related('seccion').get(pk=selected_subseccion_id)
        except Subseccion.DoesNotExist:
            messages.error(request, 'Subsección no encontrada.')
            return redirect('panel_admin:subsubseccion_list')
        
        # Obtener subsubsecciones de esta subsección
        subsubsecciones = Subsubseccion.objects.filter(subseccion=subseccion_seleccionada).annotate(
            total_prendas=Count('prendas')
        ).order_by('nombre')
        
        # Filtro de búsqueda para subsubsecciones
        search_subsubsecciones = request.GET.get('search_subsubsecciones', '')
        if search_subsubsecciones:
            subsubsecciones = subsubsecciones.filter(
                Q(nombre__icontains=search_subsubsecciones) |
                Q(descripcion__icontains=search_subsubsecciones)
            )
        
        context = {
            'title': f'Subsubsecciones de {subseccion_seleccionada.nombre}',
            'subseccion_seleccionada': subseccion_seleccionada,
            'subsubsecciones': subsubsecciones,
            'search_subsubsecciones': search_subsubsecciones,
            'step': 2,  # Indicador del paso actual
        }
    else:
        # PASO 1: Mostrar subsecciones agrupadas por sección para seleccionar
        secciones_con_subsecciones = Seccion.objects.prefetch_related(
            Prefetch(
                'subsecciones', 
                queryset=Subseccion.objects.annotate(
                    total_subsubsecciones=Count('subsubsecciones')
                ).order_by('nombre')
            )
        ).annotate(
            total_subsecciones=Count('subsecciones', distinct=True)
        ).order_by('nombre')
        
        # Filtro de búsqueda para subsecciones
        search_subsecciones = request.GET.get('search_subsecciones', '')
        
        context = {
            'title': 'Seleccionar Subsección',
            'secciones_con_subsecciones': secciones_con_subsecciones,
            'search_subsecciones': search_subsecciones,
            'step': 1,  # Indicador del paso actual
        }
    
    return render(request, 'panel_admin/subsubseccion/subsubseccion_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def subsubseccion_create(request):
    # Obtener ID de subsección desde parámetros GET
    subseccion_id = request.GET.get('subseccion_id')
    subseccion_preseleccionada = None
    
    if subseccion_id:
        try:
            subseccion_preseleccionada = Subseccion.objects.get(pk=subseccion_id)
        except Subseccion.DoesNotExist:
            subseccion_preseleccionada = None
    
    if request.method == 'POST':
        form = SubsubseccionForm(request.POST, request.FILES)
        if form.is_valid():
            subsubseccion = form.save()
            messages.success(request, 'Subsubsección creada exitosamente.')
            # Redirigir de vuelta a la lista de subsubsecciones de esa subsección
            from django.urls import reverse
            return redirect(reverse('panel_admin:subsubseccion_list') + f"?subseccion_id={subsubseccion.subseccion.id}")
    else:
        # Preseleccionar la subsección si se pasa como parámetro
        initial_data = {}
        if subseccion_preseleccionada:
            initial_data['subseccion'] = subseccion_preseleccionada
        form = SubsubseccionForm(initial=initial_data)
    
    context = {
        'title': 'Crear Subsubsección',
        'form': form,
        'action': 'crear',
        'subseccion_preseleccionada': subseccion_preseleccionada
    }
    return render(request, 'panel_admin/subsubseccion/subsubseccion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def subsubseccion_edit(request, pk):
    subsubseccion = get_object_or_404(Subsubseccion, pk=pk)
    
    if request.method == 'POST':
        form = SubsubseccionForm(request.POST, request.FILES, instance=subsubseccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subsubsección actualizada exitosamente.')
            return redirect('panel_admin:subsubseccion_list')
    else:
        form = SubsubseccionForm(instance=subsubseccion)
    
    context = {
        'title': 'Editar Subsubsección',
        'form': form,
        'subsubseccion': subsubseccion,
        'action': 'editar'
    }
    return render(request, 'panel_admin/subsubseccion/subsubseccion_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def subsubseccion_delete(request, pk):
    subsubseccion = get_object_or_404(Subsubseccion, pk=pk)
    
    if request.method == 'POST':
        subsubseccion.delete()
        messages.success(request, 'Subsubsección eliminada exitosamente.')
        return redirect('panel_admin:subsubseccion_list')
    
    context = {
        'title': 'Eliminar Subsubsección',
        'subsubseccion': subsubseccion,
    }
    return render(request, 'panel_admin/subsubseccion/subsubseccion_delete.html', context)

# =================== SUBSUBSECCIONES - VISTA POR SUBSECCIONES ===================
@login_required
@user_passes_test(is_staff_user)
def subsubseccion_list_by_subseccion(request):
    # Obtener secciones activas con sus subsecciones
    secciones = Seccion.objects.all().prefetch_related(
        'subsecciones'
    ).annotate(
        total_subsecciones=Count('subsecciones', distinct=True)
    ).order_by('nombre')
    
    context = {
        'title': 'Gestión de Subsubsecciones por Subsección',
        'secciones': secciones,
    }
    return render(request, 'panel_admin/subsubseccion/subsubseccion_by_subseccion.html', context)


@login_required
@user_passes_test(is_staff_user)
def subsubseccion_list_in_subseccion(request, subseccion_id):
    subseccion = get_object_or_404(Subseccion, pk=subseccion_id)
    
    # Obtener subsubsecciones de esta subsección
    subsubsecciones = Subsubseccion.objects.filter(subseccion=subseccion).annotate(
        total_prendas=Count('prendas')
    ).order_by('nombre')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        subsubsecciones = subsubsecciones.filter(nombre__icontains=search)
    
    # Paginación
    paginator = Paginator(subsubsecciones, 15)
    page = request.GET.get('page')
    subsubsecciones = paginator.get_page(page)
    
    context = {
        'title': f'Subsubsecciones de {subseccion.nombre}',
        'subseccion': subseccion,
        'subsubsecciones': subsubsecciones,
        'search': search,
    }
    return render(request, 'panel_admin/subsubseccion/subsubseccion_list_in_subseccion.html', context)


# =================== PRENDAS ===================

@login_required
@user_passes_test(is_staff_user)
def prenda_create(request):
    # Obtener subsubsección preseleccionada si viene desde navegación jerárquica
    subsubseccion_id = request.GET.get('subsubseccion')
    subsubseccion_preseleccionada = None
    initial_data = {}
    
    if subsubseccion_id:
        try:
            subsubseccion_preseleccionada = Subsubseccion.objects.get(pk=subsubseccion_id)
            initial_data['subsubseccion'] = subsubseccion_preseleccionada
        except Subsubseccion.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = PrendaForm(request.POST, request.FILES)
        if form.is_valid():
            prenda = form.save()
            messages.success(request, 'Prenda creada exitosamente.')
            
            # Redirigir siempre a la subsubsección de la prenda creada
            return redirect('panel_admin:prenda_list_in_subsubseccion', prenda.subsubseccion.id)
    else:
        form = PrendaForm(initial=initial_data)
    
    context = {
        'title': 'Crear Prenda',
        'form': form,
        'action': 'crear',
        'subsubseccion_preseleccionada': subsubseccion_preseleccionada
    }
    return render(request, 'panel_admin/prenda/prenda_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def prenda_edit(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)
    
    if request.method == 'POST':
        form = PrendaForm(request.POST, request.FILES, instance=prenda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prenda actualizada exitosamente.')
            # Redirigir a la subsubsección de la prenda editada
            return redirect('panel_admin:prenda_list_in_subsubseccion', prenda.subsubseccion.id)
    else:
        form = PrendaForm(instance=prenda)
    
    context = {
        'title': 'Editar Prenda',
        'form': form,
        'prenda': prenda,
        'action': 'editar',
        'subsubseccion_preseleccionada': prenda.subsubseccion
    }
    return render(request, 'panel_admin/prenda/prenda_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def prenda_delete(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)
    subsubseccion_id = prenda.subsubseccion.id  # Guardar el ID antes de eliminar
    
    if request.method == 'POST':
        prenda.delete()
        messages.success(request, 'Prenda eliminada exitosamente.')
        # Redirigir a la subsubsección de la prenda eliminada
        return redirect('panel_admin:prenda_list_in_subsubseccion', subsubseccion_id)
    
    context = {
        'title': 'Eliminar Prenda',
        'prenda': prenda,
    }
    return render(request, 'panel_admin/prenda/prenda_delete.html', context)

# =================== PRENDAS - VISTA JERÁRQUICA ===================
@login_required
@user_passes_test(is_staff_user)
def prenda_list_by_subseccion(request):
    """Vista principal de prendas organizadas por subsección"""
    # Obtener secciones activas con conteo correcto
    secciones = Seccion.objects.all().annotate(
        total_subsecciones=Count('subsecciones', distinct=True),
        total_prendas=Count('subsecciones__subsubsecciones__prendas', distinct=True)
    ).order_by('nombre')
    
    context = {
        'title': 'Gestión de Prendas por Subsección',
        'secciones': secciones,
    }
    return render(request, 'panel_admin/prenda/prenda_by_subseccion.html', context)


@login_required
@user_passes_test(is_staff_user)
def prenda_list_by_subsubseccion(request, subseccion_id):
    """Vista de subsubsecciones de una subsección con sus prendas"""
    subseccion = get_object_or_404(Subseccion, pk=subseccion_id)
    
    # Obtener subsubsecciones de esta subsección con conteo de prendas
    subsubsecciones = Subsubseccion.objects.filter(subseccion=subseccion).prefetch_related(
        'prendas'
    ).annotate(
        total_prendas=Count('prendas', )
    ).order_by('nombre')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        subsubsecciones = subsubsecciones.filter(nombre__icontains=search)
    
    # Paginación
    paginator = Paginator(subsubsecciones, 12)
    page = request.GET.get('page')
    subsubsecciones = paginator.get_page(page)
    
    context = {
        'title': f'Prendas de {subseccion.nombre}',
        'subseccion': subseccion,
        'subsubsecciones': subsubsecciones,
        'search': search,
    }
    return render(request, 'panel_admin/prenda/prenda_by_subsubseccion.html', context)


@login_required
@user_passes_test(is_staff_user)
def prenda_list_in_subsubseccion(request, subsubseccion_id):
    """Vista de prendas de una subsubsección específica"""
    subsubseccion = get_object_or_404(Subsubseccion, pk=subsubseccion_id)
    
    # Obtener prendas de esta subsubsección
    prendas = Prenda.objects.filter(subsubseccion=subsubseccion).order_by('-creado_en')
    
    # Paginación
    paginator = Paginator(prendas, 12)
    page = request.GET.get('page')
    prendas = paginator.get_page(page)
    
    context = {
        'title': f'Prendas de {subsubseccion.nombre}',
        'subsubseccion': subsubseccion,
        'prendas': prendas,
    }
    return render(request, 'panel_admin/prenda/prenda_in_subsubseccion.html', context)


@login_required
@user_passes_test(is_staff_user)
def prenda_multiple_upload(request, subsubseccion_id):
    """Vista para subida múltiple de prendas"""
    subsubseccion = get_object_or_404(Subsubseccion, pk=subsubseccion_id)
    
    if request.method == 'POST':
        form = PrendaMultipleUploadForm(request.POST, request.FILES, subsubseccion_id=subsubseccion_id)
        
        if form.is_valid():
            images = request.FILES.getlist('imagenes')
            precio = form.cleaned_data['precio']
            target_subsubseccion = form.cleaned_data['subsubseccion']
            
            # Generar fecha para el nombre
            today = datetime.now()
            fecha_str = f"{today.day:02d}-{today.month:02d}-{today.year}"
            
            prendas_creadas = []
            for i, image in enumerate(images, 1):
                # Generar nombre único: nombresubsubseccion-dia-mes-año-numero
                nombre = f"{target_subsubseccion.nombre.lower().replace(' ', '-')}-{fecha_str}-{i}"
                
                # Crear la prenda
                prenda = Prenda.objects.create(
                    nombre=nombre,
                    subsubseccion=target_subsubseccion,
                    imagen=image,
                    precio=precio
                )
                prendas_creadas.append(prenda)
            
            messages.success(
                request, 
                f'Se han creado exitosamente {len(prendas_creadas)} prendas en {target_subsubseccion.nombre}.'
            )
            return redirect('panel_admin:prenda_list_in_subsubseccion', subsubseccion_id=target_subsubseccion.id)
        
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    
    else:
        form = PrendaMultipleUploadForm(subsubseccion_id=subsubseccion_id)
    
    context = {
        'title': f'Subida múltiple - {subsubseccion.nombre}',
        'subsubseccion': subsubseccion,
        'form': form,
        'action': 'subida_multiple'
    }
    return render(request, 'panel_admin/prenda/prenda_multiple_upload.html', context)