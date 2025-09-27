"""
Sistema de programación automática para envío de códigos de descuento
Usa APScheduler para ejecutar tareas automáticas sin necesidad de cronjobs
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import ConfiguracionDescuentos, User, CarritoItem, CodigoDescuento
from .utils import enviar_email_codigo_descuento
import atexit

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancia global del scheduler
scheduler = None

def get_scheduler():
    """Obtener la instancia global del scheduler"""
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        # Registrar para que se cierre cuando termine la aplicación
        atexit.register(lambda: scheduler.shutdown() if scheduler else None)
    return scheduler

def enviar_codigos_inactivos():
    """
    Función que se ejecuta automáticamente para enviar códigos a usuarios inactivos
    """
    try:
        logger.info("🤖 Iniciando proceso automático de envío de códigos...")

        # Obtener configuración activa
        config = ConfiguracionDescuentos.objects.filter(activo=True).first()

        if not config:
            logger.warning("⚠️  No hay configuración activa. Proceso cancelado.")
            return

        # Calcular fecha límite de inactividad
        fecha_limite = timezone.now() - timedelta(days=config.dias_inactividad)

        # Encontrar usuarios con items en carrito pero sin actividad reciente
        usuarios_inactivos = User.objects.filter(
            carrito_items__isnull=False,
            carrito_items__ultima_actividad__lt=fecha_limite,
            profile__isnull=False
        ).distinct()

        codigos_enviados = 0
        errores = 0

        for usuario in usuarios_inactivos:
            try:
                # Verificar que no tenga códigos activos ya
                codigos_existentes = CodigoDescuento.objects.filter(
                    user=usuario,
                    usado=False
                ).filter(
                    fecha_expiracion__isnull=True
                ) | CodigoDescuento.objects.filter(
                    user=usuario,
                    usado=False,
                    fecha_expiracion__gt=timezone.now()
                )

                if codigos_existentes.exists():
                    logger.info(f"👤 Usuario {usuario.profile.instagram_account} ya tiene códigos activos")
                    continue

                # Crear código de descuento
                codigo = CodigoDescuento.objects.create(
                    user=usuario,
                    porcentaje=config.porcentaje_descuento,
                    fecha_expiracion=None  # Sin expiración para códigos automáticos
                )

                # Enviar email si está configurado
                items_carrito = CarritoItem.objects.filter(user=usuario)
                success = enviar_email_codigo_descuento(
                    usuario=usuario,
                    codigo=codigo,
                    items_carrito=items_carrito
                )

                if success:
                    codigos_enviados += 1
                    logger.info(f"✅ Código {codigo.codigo} enviado a {usuario.profile.instagram_account}")
                else:
                    logger.warning(f"⚠️  Código creado pero email falló para {usuario.profile.instagram_account}")
                    codigos_enviados += 1  # Contar como enviado aunque el email falle

            except Exception as e:
                errores += 1
                logger.error(f"❌ Error procesando usuario {usuario.id}: {str(e)}")

        logger.info(f"🎯 Proceso completado: {codigos_enviados} códigos enviados, {errores} errores")

        # Opcional: Guardar estadísticas en base de datos
        # Puedes crear un modelo para esto si quieres tracking

    except Exception as e:
        logger.error(f"💥 Error crítico en proceso automático: {str(e)}")

def iniciar_scheduler():
    """
    Iniciar el scheduler con las tareas automáticas
    """
    try:
        scheduler = get_scheduler()

        # Verificar si ya está ejecutándose
        if scheduler.running:
            logger.info("📋 Scheduler ya está ejecutándose")
            return True

        # Obtener configuración activa
        config = ConfiguracionDescuentos.objects.filter(activo=True).first()

        if not config or not config.activo:
            logger.info("⏸️  Sistema desactivado, no se iniciará el scheduler")
            return False

        # Limpiar trabajos existentes
        scheduler.remove_all_jobs()

        # Agregar trabajo para enviar códigos diariamente a las 10:00 AM
        scheduler.add_job(
            func=enviar_codigos_inactivos,
            trigger=CronTrigger(hour=10, minute=0),  # Todos los días a las 10:00
            id='envio_codigos_diario',
            name='Envío automático de códigos de descuento',
            replace_existing=True,
            max_instances=1  # Solo una instancia a la vez
        )

        # Iniciar scheduler
        scheduler.start()
        logger.info("🚀 Scheduler iniciado correctamente - Ejecutará diariamente a las 10:00 AM")
        return True

    except Exception as e:
        logger.error(f"💥 Error iniciando scheduler: {str(e)}")
        return False

def detener_scheduler():
    """
    Detener el scheduler
    """
    try:
        scheduler = get_scheduler()

        if scheduler.running:
            # Limpiar trabajos
            scheduler.remove_all_jobs()
            scheduler.shutdown(wait=False)
            logger.info("⏹️  Scheduler detenido correctamente")
            return True
        else:
            logger.info("📋 Scheduler ya está detenido")
            return True

    except Exception as e:
        logger.error(f"💥 Error deteniendo scheduler: {str(e)}")
        return False

def reiniciar_scheduler():
    """
    Reiniciar el scheduler (detener y volver a iniciar)
    """
    logger.info("🔄 Reiniciando scheduler...")
    detener_scheduler()
    return iniciar_scheduler()

def estado_scheduler():
    """
    Obtener el estado actual del scheduler
    """
    try:
        scheduler = get_scheduler()

        if scheduler.running:
            jobs = scheduler.get_jobs()
            return {
                'activo': True,
                'trabajos': len(jobs),
                'proximo_envio': jobs[0].next_run_time if jobs else None
            }
        else:
            return {
                'activo': False,
                'trabajos': 0,
                'proximo_envio': None
            }
    except Exception as e:
        logger.error(f"Error obteniendo estado: {str(e)}")
        return {
            'activo': False,
            'trabajos': 0,
            'proximo_envio': None,
            'error': str(e)
        }

# Función para ejecutar manualmente (testing)
def ejecutar_envio_manual():
    """
    Ejecutar el envío de códigos manualmente para testing
    """
    logger.info("🔧 Ejecutando envío manual...")
    enviar_codigos_inactivos()