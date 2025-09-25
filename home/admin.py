from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Seccion, Subseccion, Subsubseccion, Prenda, UserProfile, CarritoItem, CodigoDescuento, ConfiguracionDescuentos


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'instagram_account', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username', 'instagram_account')
    readonly_fields = ('created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user',) + self.readonly_fields
        return self.readonly_fields


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'creado_en')
    list_filter = ('creado_en',)
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('creado_en',)


@admin.register(Subseccion)
class SubseccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'seccion', 'creado_en')
    list_filter = ('seccion', 'creado_en')
    search_fields = ('nombre', 'descripcion', 'seccion__nombre')
    readonly_fields = ('creado_en',)


@admin.register(Subsubseccion)
class SubsubseccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'subseccion', 'creado_en')
    list_filter = ('subseccion__seccion', 'subseccion', 'creado_en')
    search_fields = ('nombre', 'descripcion', 'subseccion__nombre')
    readonly_fields = ('creado_en',)


@admin.register(Prenda)
class PrendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'subsubseccion', 'precio', 'creado_en')
    list_filter = ('subsubseccion__subseccion__seccion', 'subsubseccion__subseccion', 'creado_en')
    search_fields = ('nombre', 'subsubseccion__nombre')
    readonly_fields = ('creado_en',)


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('usuario_instagram', 'prenda_nombre', 'agregado_en', 'ultima_actividad', 'dias_inactivo')
    list_filter = ('agregado_en', 'ultima_actividad', 'prenda__subsubseccion__subseccion__seccion')
    search_fields = ('user__profile__instagram_account', 'user__email', 'prenda__nombre')
    readonly_fields = ('agregado_en', 'ultima_actividad')

    def usuario_instagram(self, obj):
        if obj.user.profile:
            return format_html(
                '<a href="{}" target="_blank">@{}</a><br><small>{}</small>',
                f"https://www.instagram.com/{obj.user.profile.instagram_account}",
                obj.user.profile.instagram_account,
                obj.user.email
            )
        return obj.user.email
    usuario_instagram.short_description = "Usuario"

    def prenda_nombre(self, obj):
        nombre = obj.prenda.nombre or f"Prenda de {obj.prenda.subsubseccion.nombre}"
        precio = f" - {obj.prenda.precio}€" if obj.prenda.precio else ""
        return f"{nombre}{precio}"
    prenda_nombre.short_description = "Prenda"

    def dias_inactivo(self, obj):
        dias = (timezone.now() - obj.ultima_actividad).days
        if dias > 3:
            return format_html('<span style="color: red;">⚠️ {} días</span>', dias)
        elif dias > 1:
            return format_html('<span style="color: orange;">⚠️ {} días</span>', dias)
        return f"{dias} días"
    dias_inactivo.short_description = "Inactivo"


@admin.register(CodigoDescuento)
class CodigoDescuentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario_instagram', 'porcentaje', 'usado', 'email_enviado', 'fecha_creacion', 'fecha_expiracion', 'estado_vigente')
    list_filter = ('usado', 'email_enviado', 'fecha_creacion', 'porcentaje')
    search_fields = ('codigo', 'user__profile__instagram_account', 'user__email')
    readonly_fields = ('codigo', 'fecha_creacion', 'fecha_uso')

    def usuario_instagram(self, obj):
        if obj.user.profile:
            return format_html(
                '<a href="{}" target="_blank">@{}</a><br><small>{}</small>',
                f"https://www.instagram.com/{obj.user.profile.instagram_account}",
                obj.user.profile.instagram_account,
                obj.user.email
            )
        return obj.user.email
    usuario_instagram.short_description = "Usuario"

    def estado_vigente(self, obj):
        if obj.usado:
            return format_html('<span style="color: gray;">✓ Usado</span>')
        elif obj.esta_vigente:
            return format_html('<span style="color: green;">✓ Vigente</span>')
        else:
            return format_html('<span style="color: red;">✗ Expirado</span>')
    estado_vigente.short_description = "Estado"

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.usado:  # Si ya está usado, hacer más campos readonly
            return self.readonly_fields + ('user', 'porcentaje', 'fecha_expiracion')
        return self.readonly_fields


@admin.register(ConfiguracionDescuentos)
class ConfiguracionDescuentosAdmin(admin.ModelAdmin):
    list_display = ('dias_inactividad', 'porcentaje_descuento', 'activo', 'creado_en', 'actualizado_en')
    list_filter = ('activo', 'creado_en')
    readonly_fields = ('creado_en', 'actualizado_en')

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración activa
        if obj and obj.activo:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if obj.activo:
            # Desactivar otras configuraciones
            ConfiguracionDescuentos.objects.filter(activo=True).update(activo=False)
        super().save_model(request, obj, form, change)
