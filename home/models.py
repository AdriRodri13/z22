from django.db import models
from .utils import seleccionar_storage

class Temporada(models.Model):
    nombre = models.CharField(max_length=20)  
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        get_latest_by = 'creado_en'


class Liga(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(
        storage=seleccionar_storage(),
        upload_to='LogoLiga/',
        blank=True,
        null=True
    )
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name='ligas')

    def __str__(self):
        return f"{self.nombre} ({self.pais.nombre})"


class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(
        storage=seleccionar_storage(),
        upload_to='LogoEquipos/',
        blank=True,
        null=True
    )
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE, related_name='equipos')

    def __str__(self):
        return f"{self.nombre} - {self.liga.nombre}"


class Equipacion(models.Model):

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='equipaciones')
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name='equipaciones')
    imagen = models.ImageField(
        storage=seleccionar_storage(),
        upload_to='equipaciones/',
        blank=True,
        null=True
    )

