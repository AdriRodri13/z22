from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('seccion/<int:seccion_id>/', views.seccion_detail, name='seccion_detail'),
    path('subseccion/<int:subseccion_id>/', views.subseccion_detail, name='subseccion_detail'),
    path('subsubseccion/<int:subsubseccion_id>/', views.subsubseccion_detail, name='subsubseccion_detail'),
    path('consultar-disponibilidad/', views.consultar_disponibilidad, name='consultar_disponibilidad'),
    path('registro/', views.registro_view, name='registro'),
    path('rechazar-registro/', views.rechazar_registro, name='rechazar_registro'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    # URLs del carrito
    path('carrito/agregar/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/remover/', views.remover_carrito, name='remover_carrito'),
    path('carrito/obtener/', views.obtener_carrito, name='obtener_carrito'),
]