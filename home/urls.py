from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='index'),
    path('liga/<int:liga_id>/', views.liga_detail, name='liga_detail'),
    path('equipo/<int:equipo_id>/', views.equipo_detail, name='equipo_detail'),
]