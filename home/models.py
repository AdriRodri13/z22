from django.db import models
from .utils import seleccionar_storage


class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, blank=True, null=True, help_text="Clase CSS del icono (ej: fas fa-tshirt)", default='')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
        ordering = ['nombre']


class Subseccion(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(
        storage=seleccionar_storage(),
        upload_to='logos/subsecciones/',
        blank=True,
        null=True
    )
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='subsecciones')
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.seccion.nombre}"
    
    class Meta:
        verbose_name = "Subsección"
        verbose_name_plural = "Subsecciones"
        ordering = ['nombre']


class Subsubseccion(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(
        storage=seleccionar_storage(),
        upload_to='logos/subsubsecciones/',
        blank=True,
        null=True
    )
    subseccion = models.ForeignKey(Subseccion, on_delete=models.CASCADE, related_name='subsubsecciones')
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.subseccion.nombre}"
    
    class Meta:
        verbose_name = "Subsubsección"
        verbose_name_plural = "Subsubsecciones"
        ordering = ['nombre']


class Prenda(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True, help_text="Nombre opcional de la prenda")
    subsubseccion = models.ForeignKey(Subsubseccion, on_delete=models.CASCADE, related_name='prendas')
    imagen = models.ImageField(
        storage=seleccionar_storage(),
        upload_to='prendas/',
        blank=True,
        null=True
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.nombre:
            return f"{self.nombre} - {self.subsubseccion.nombre}"
        return f"Prenda de {self.subsubseccion.nombre}"
    
    class Meta:
        verbose_name = "Prenda"
        verbose_name_plural = "Prendas"
        ordering = ['-creado_en']

