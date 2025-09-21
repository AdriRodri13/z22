from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('seccion/<int:seccion_id>/', views.seccion_detail, name='seccion_detail'),
    path('subseccion/<int:subseccion_id>/', views.subseccion_detail, name='subseccion_detail'),
    path('subsubseccion/<int:subsubseccion_id>/', views.subsubseccion_detail, name='subsubseccion_detail'),
    path('consultar-disponibilidad/', views.consultar_disponibilidad, name='consultar_disponibilidad'),
]