from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'panel_admin'

urlpatterns = [
    # Autenticación
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='panel_admin:login'), name='logout'),
    
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de Secciones
    path('secciones/', views.seccion_list, name='seccion_list'),
    path('secciones/crear/', views.seccion_create, name='seccion_create'),
    path('secciones/<int:pk>/editar/', views.seccion_edit, name='seccion_edit'),
    path('secciones/<int:pk>/eliminar/', views.seccion_delete, name='seccion_delete'),
    
    # Gestión de Subsecciones
    path('subsecciones/', views.subseccion_list, name='subseccion_list'),
    path('subsecciones/crear/', views.subseccion_create, name='subseccion_create'),
    path('subsecciones/<int:pk>/editar/', views.subseccion_edit, name='subseccion_edit'),
    path('subsecciones/<int:pk>/eliminar/', views.subseccion_delete, name='subseccion_delete'),
    
    # Gestión de Subsubsecciones
    path('subsubsecciones/', views.subsubseccion_list_by_subseccion, name='subsubseccion_list_by_subseccion'),  # Vista principal por subsecciones
    path('subsubsecciones/lista/', views.subsubseccion_list_by_subseccion, name='subsubseccion_list'),  # Alias para compatibilidad
    path('subsubsecciones/todos/', views.subsubseccion_list, name='subsubseccion_list_all'),  # Vista de tabla completa
    path('subsubsecciones/subseccion/<int:subseccion_id>/', views.subsubseccion_list_in_subseccion, name='subsubseccion_list_in_subseccion'),  # Subsubsecciones de una subsección específica
    path('subsubsecciones/crear/', views.subsubseccion_create, name='subsubseccion_create'),
    path('subsubsecciones/<int:pk>/editar/', views.subsubseccion_edit, name='subsubseccion_edit'),
    path('subsubsecciones/<int:pk>/eliminar/', views.subsubseccion_delete, name='subsubseccion_delete'),
    
    # Gestión de Prendas - Vista jerárquica
    path('prendas/', views.prenda_list_by_subseccion, name='prenda_list_by_subseccion'),  # Vista principal por subsecciones
    path('prendas/lista/', views.prenda_list_by_subseccion, name='prenda_list'),  # Alias para compatibilidad
    path('prendas/subseccion/<int:subseccion_id>/', views.prenda_list_by_subsubseccion, name='prenda_list_by_subsubseccion'),  # Subsubsecciones de una subsección
    path('prendas/subsubseccion/<int:subsubseccion_id>/', views.prenda_list_in_subsubseccion, name='prenda_list_in_subsubseccion'),  # Prendas de una subsubsección
    path('prendas/subsubseccion/<int:subsubseccion_id>/subida-multiple/', views.prenda_multiple_upload, name='prenda_multiple_upload'),  # Subida múltiple
    path('prendas/crear/', views.prenda_create, name='prenda_create'),
    path('prendas/<int:pk>/editar/', views.prenda_edit, name='prenda_edit'),
    path('prendas/<int:pk>/eliminar/', views.prenda_delete, name='prenda_delete'),

    # Gestión de Usuarios y Descuentos
    path('usuarios-descuentos/', views.usuarios_descuentos_dashboard, name='usuarios_descuentos_dashboard'),
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/<int:user_id>/', views.usuario_detail, name='usuario_detail'),
    path('codigos-descuento/', views.codigos_descuento_list, name='codigos_descuento_list'),
    path('codigos-descuento/crear/', views.crear_codigo_descuento, name='crear_codigo_descuento'),
    path('configuracion-descuentos/', views.configuracion_descuentos, name='configuracion_descuentos'),
    path('enviar-codigos/', views.enviar_codigos_manual, name='enviar_codigos_manual'),
]