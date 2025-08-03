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
    
    # Gestión de Temporadas
    path('temporadas/', views.temporada_list, name='temporada_list'),
    path('temporadas/crear/', views.temporada_create, name='temporada_create'),
    path('temporadas/<int:pk>/editar/', views.temporada_edit, name='temporada_edit'),
    path('temporadas/<int:pk>/eliminar/', views.temporada_delete, name='temporada_delete'),
    
    # Gestión de Ligas
    path('ligas/', views.liga_list, name='liga_list'),
    path('ligas/crear/', views.liga_create, name='liga_create'),
    path('ligas/<int:pk>/editar/', views.liga_edit, name='liga_edit'),
    path('ligas/<int:pk>/eliminar/', views.liga_delete, name='liga_delete'),
    
    # Gestión de Equipos
    path('equipos/', views.equipo_list_by_liga, name='equipo_list'),  # Vista principal por ligas
    path('equipos/todos/', views.equipo_list, name='equipo_list_all'),  # Vista de tabla completa
    path('equipos/liga/<int:liga_id>/', views.equipo_list_in_liga, name='equipo_list_in_liga'),  # Equipos de una liga específica
    path('equipos/crear/', views.equipo_create, name='equipo_create'),
    path('equipos/<int:pk>/editar/', views.equipo_edit, name='equipo_edit'),
    path('equipos/<int:pk>/eliminar/', views.equipo_delete, name='equipo_delete'),
    
    # Gestión de Equipaciones - Vista jerárquica
    path('equipaciones/', views.equipacion_list_by_liga, name='equipacion_list'),  # Vista principal por ligas
    path('equipaciones/liga/<int:liga_id>/', views.equipacion_list_by_equipo, name='equipacion_list_by_equipo'),  # Equipos de una liga
    path('equipaciones/equipo/<int:equipo_id>/', views.equipacion_list_in_equipo, name='equipacion_list_in_equipo'),  # Equipaciones de un equipo
    path('equipaciones/crear/', views.equipacion_create, name='equipacion_create'),
    path('equipaciones/<int:pk>/editar/', views.equipacion_edit, name='equipacion_edit'),
    path('equipaciones/<int:pk>/eliminar/', views.equipacion_delete, name='equipacion_delete'),
]