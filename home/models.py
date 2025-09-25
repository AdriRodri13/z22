from django.db import models
from django.contrib.auth.models import User
from .utils import seleccionar_storage


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    instagram_account = models.CharField(max_length=100, unique=True, help_text="Cuenta de Instagram sin @")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.instagram_account} - {self.user.email}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"


class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    logo = models.ImageField(
        storage=seleccionar_storage(),
        upload_to='logos/secciones/',
        blank=True,
        null=True
    )
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


class CarritoItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrito_items')
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='carrito_items')
    agregado_en = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.profile.instagram_account} - {self.prenda}"

    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = ('user', 'prenda')
        ordering = ['-ultima_actividad']


class ConfiguracionDescuentos(models.Model):
    dias_inactividad = models.PositiveIntegerField(default=3, help_text="Días de inactividad antes de enviar código")
    porcentaje_descuento = models.PositiveIntegerField(default=10, help_text="Porcentaje de descuento (0-100)")
    activo = models.BooleanField(default=True, help_text="Si el sistema de descuentos está activo")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Config: {self.dias_inactividad} días - {self.porcentaje_descuento}%"

    class Meta:
        verbose_name = "Configuración de Descuentos"
        verbose_name_plural = "Configuración de Descuentos"
        ordering = ['-creado_en']

    def save(self, *args, **kwargs):
        # Solo permitir una configuración activa
        if self.activo:
            ConfiguracionDescuentos.objects.filter(activo=True).update(activo=False)
        super().save(*args, **kwargs)


class CodigoDescuento(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='codigos_descuento')
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único de descuento")
    porcentaje = models.PositiveIntegerField(help_text="Porcentaje de descuento")
    usado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    fecha_uso = models.DateTimeField(null=True, blank=True)
    email_enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.codigo} - @{self.user.profile.instagram_account} ({self.porcentaje}%)"

    class Meta:
        verbose_name = "Código de Descuento"
        verbose_name_plural = "Códigos de Descuento"
        ordering = ['-fecha_creacion']

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único
            import random
            import string
            while True:
                codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not CodigoDescuento.objects.filter(codigo=codigo).exists():
                    self.codigo = codigo
                    break
        super().save(*args, **kwargs)

    @property
    def esta_vigente(self):
        if self.usado:
            return False
        if self.fecha_expiracion:
            from django.utils import timezone
            return timezone.now() < self.fecha_expiracion
        return True

