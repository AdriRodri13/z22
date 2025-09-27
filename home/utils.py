"""
Utilidades para el sistema de descuentos y configuración de almacenamiento
"""

from django.conf import settings
from django.core.files.storage import default_storage


def seleccionar_storage():
    """
    Seleccionar el storage apropiado basado en la configuración
    """
    try:
        if not settings.DEBUG and hasattr(settings, 'CLOUDINARY_STORAGE') and settings.CLOUDINARY_STORAGE:
            from cloudinary_storage.storage import MediaCloudinaryStorage
            return MediaCloudinaryStorage()
        else:
            return default_storage
    except ImportError:
        # Si cloudinary no está disponible, usar storage por defecto
        return default_storage

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_email_codigo_descuento(usuario, codigo, items_carrito=None):
    """
    Enviar email con código de descuento a un usuario

    Args:
        usuario: User instance
        codigo: CodigoDescuento instance
        items_carrito: QuerySet de CarritoItem (opcional)

    Returns:
        bool: True si se envió correctamente, False si hubo error
    """
    try:
        # Datos para el template
        context = {
            'usuario': usuario,
            'codigo': codigo,
            'items_carrito': items_carrito,
            'nombre_tienda': 'Cesta Trend',  # Personalizar según tu tienda
        }

        # Renderizar el email
        asunto = f'🎁 ¡Tienes un descuento del {codigo.porcentaje}%! - Cesta Trend'

        # Mensaje de texto plano
        mensaje_texto = f"""
¡Hola @{usuario.profile.instagram_account}!

¡Tenemos una sorpresa para ti! 🎉

Hemos notado que tienes algunos productos increíbles en tu carrito, pero aún no has completado tu compra.
Para ayudarte a decidirte, te regalamos un código de descuento especial:

🎟️ CÓDIGO: {codigo.codigo}
💰 DESCUENTO: {codigo.porcentaje}%

{"🛒 Productos en tu carrito:" if items_carrito else ""}
"""

        if items_carrito:
            for item in items_carrito:
                mensaje_texto += f"• {item.prenda.nombre} - ${item.prenda.precio}\n"

        mensaje_texto += f"""

¡No dejes pasar esta oportunidad! Tu código es válido {"por tiempo limitado" if codigo.fecha_expiracion else "sin fecha de expiración"}.

Visita nuestra tienda y completa tu compra ahora:
[Enlace a tu tienda]

¡Gracias por elegirnos!
El equipo de Cesta Trend

---
Si no deseas recibir estos emails, puedes darte de baja en cualquier momento.
"""

        # Enviar email
        resultado = send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            fail_silently=False,
        )

        if resultado:
            logger.info(f"📧 Email enviado correctamente a {usuario.profile.instagram_account}")
            return True
        else:
            logger.warning(f"⚠️  Email no se pudo enviar a {usuario.profile.instagram_account}")
            return False

    except Exception as e:
        logger.error(f"❌ Error enviando email a {usuario.profile.instagram_account}: {str(e)}")
        return False

def validar_configuracion_email():
    """
    Validar que la configuración de email esté correcta

    Returns:
        dict: Resultado de la validación con información del estado
    """
    try:
        # Verificar configuraciones básicas
        configuraciones = {
            'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
            'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
            'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
            'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        }

        # Verificar que las configuraciones críticas estén presentes
        configuraciones_faltantes = []
        for clave, valor in configuraciones.items():
            if not valor:
                configuraciones_faltantes.append(clave)

        if configuraciones_faltantes:
            return {
                'valido': False,
                'error': f'Configuraciones de email faltantes: {", ".join(configuraciones_faltantes)}',
                'configuraciones': configuraciones
            }

        return {
            'valido': True,
            'mensaje': 'Configuración de email válida',
            'configuraciones': configuraciones
        }

    except Exception as e:
        return {
            'valido': False,
            'error': f'Error validando configuración: {str(e)}',
            'configuraciones': {}
        }

def obtener_estadisticas_envios():
    """
    Obtener estadísticas de códigos enviados

    Returns:
        dict: Estadísticas de envíos
    """
    try:
        from .models import CodigoDescuento
        from django.utils import timezone
        from datetime import timedelta

        # Estadísticas generales
        total_codigos = CodigoDescuento.objects.count()
        codigos_usados = CodigoDescuento.objects.filter(usado=True).count()
        codigos_activos = CodigoDescuento.objects.filter(
            usado=False,
            fecha_expiracion__isnull=True
        ).count() + CodigoDescuento.objects.filter(
            usado=False,
            fecha_expiracion__gt=timezone.now()
        ).count()

        # Estadísticas de los últimos 7 días
        hace_semana = timezone.now() - timedelta(days=7)
        codigos_semana = CodigoDescuento.objects.filter(
            fecha_creacion__gte=hace_semana
        ).count()

        # Estadísticas de hoy
        hoy = timezone.now().date()
        codigos_hoy = CodigoDescuento.objects.filter(
            fecha_creacion__date=hoy
        ).count()

        return {
            'total_codigos': total_codigos,
            'codigos_usados': codigos_usados,
            'codigos_activos': codigos_activos,
            'codigos_ultima_semana': codigos_semana,
            'codigos_hoy': codigos_hoy,
            'tasa_uso': round((codigos_usados / total_codigos * 100), 2) if total_codigos > 0 else 0
        }

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return {
            'error': str(e),
            'total_codigos': 0,
            'codigos_usados': 0,
            'codigos_activos': 0,
            'codigos_ultima_semana': 0,
            'codigos_hoy': 0,
            'tasa_uso': 0
        }