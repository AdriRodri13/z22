from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        """
        Se ejecuta cuando Django está completamente cargado
        Aquí inicializamos el scheduler automático
        """
        try:
            # Solo importar aquí para evitar problemas de dependencias circulares
            from .scheduler import iniciar_scheduler
            from .models import ConfiguracionDescuentos

            # Verificar si hay configuración activa
            try:
                config = ConfiguracionDescuentos.objects.filter(activo=True).first()
                if config and config.activo:
                    logger.info("🚀 Iniciando scheduler automático...")
                    iniciar_scheduler()
                else:
                    logger.info("⏸️  Sistema de descuentos desactivado, scheduler no iniciado")
            except Exception as db_error:
                # Durante migraciones la BD puede no estar lista
                logger.info(f"📊 Base de datos no disponible aún: {str(db_error)}")

        except Exception as e:
            logger.error(f"💥 Error inicializando scheduler en apps.py: {str(e)}")
