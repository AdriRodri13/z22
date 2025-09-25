from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from home.models import CarritoItem, CodigoDescuento, ConfiguracionDescuentos, UserProfile
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Envía códigos de descuento a usuarios con carrito inactivo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué usuarios recibirían el código, sin enviarlo',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Enviar códigos incluso si ya tienen uno vigente',
        )

    def handle(self, *args, **options):
        # Obtener configuración activa
        try:
            config = ConfiguracionDescuentos.objects.filter(activo=True).first()
            if not config:
                self.stdout.write(
                    self.style.ERROR('No hay configuración de descuentos activa')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al obtener configuración: {str(e)}')
            )
            return

        dias_inactividad = config.dias_inactividad
        porcentaje_descuento = config.porcentaje_descuento

        # Calcular fecha límite de inactividad
        fecha_limite = timezone.now() - timedelta(days=dias_inactividad)

        self.stdout.write(f'Buscando usuarios inactivos desde: {fecha_limite}')
        self.stdout.write(f'Configuración: {dias_inactividad} días, {porcentaje_descuento}% descuento')

        # Encontrar usuarios con elementos en carrito pero sin actividad reciente
        usuarios_inactivos = User.objects.filter(
            carrito_items__ultima_actividad__lt=fecha_limite,
            profile__isnull=False
        ).distinct()

        # Filtrar usuarios que ya tienen un código vigente (a menos que se use --force)
        if not options['force']:
            usuarios_con_codigo = User.objects.filter(
                codigos_descuento__usado=False,
                codigos_descuento__fecha_expiracion__gt=timezone.now()
            ).values_list('id', flat=True)

            usuarios_inactivos = usuarios_inactivos.exclude(id__in=usuarios_con_codigo)

        self.stdout.write(f'Usuarios inactivos encontrados: {usuarios_inactivos.count()}')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN - No se enviarán emails'))

        emails_enviados = 0
        errores = 0

        for usuario in usuarios_inactivos:
            try:
                # Obtener todos los items del carrito del usuario
                carrito_items = CarritoItem.objects.filter(user=usuario).select_related('prenda')

                if not carrito_items.exists():
                    continue

                # Crear código de descuento
                if not options['dry_run']:
                    codigo_descuento = CodigoDescuento.objects.create(
                        user=usuario,
                        porcentaje=porcentaje_descuento,
                        fecha_expiracion=timezone.now() + timedelta(days=30)  # 30 días para usar el código
                    )

                # Preparar datos para el email
                items_data = []
                for item in carrito_items:
                    items_data.append({
                        'nombre': item.prenda.nombre or f"Prenda de {item.prenda.subsubseccion.nombre}",
                        'precio': f"{item.prenda.precio}€" if item.prenda.precio else 'Precio no disponible',
                        'imagen_url': item.prenda.imagen.url if item.prenda.imagen else '',
                        'subsubseccion': item.prenda.subsubseccion.nombre,
                        'subseccion': item.prenda.subsubseccion.subseccion.nombre,
                        'seccion': item.prenda.subsubseccion.subseccion.seccion.nombre,
                        'agregado_en': item.agregado_en,
                        'ultima_actividad': item.ultima_actividad
                    })

                if options['dry_run']:
                    self.stdout.write(
                        f'  → {usuario.profile.instagram_account} ({usuario.email}) - '
                        f'{len(items_data)} items en carrito'
                    )
                    continue

                # Crear contexto para el template del email
                context = {
                    'usuario': usuario,
                    'instagram_account': usuario.profile.instagram_account,
                    'codigo_descuento': codigo_descuento.codigo,
                    'porcentaje_descuento': porcentaje_descuento,
                    'items_carrito': items_data,
                    'cantidad_items': len(items_data),
                    'fecha_expiracion': codigo_descuento.fecha_expiracion,
                    'dias_inactivo': dias_inactividad
                }

                # Renderizar email HTML
                html_message = render_to_string('emails/codigo_descuento.html', context)
                plain_message = strip_tags(html_message)

                # Enviar email
                subject = f'¡{porcentaje_descuento}% de descuento para ti! - Zone22'

                send_mail(
                    subject=subject,
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],
                    fail_silently=False,
                )

                # Marcar como enviado
                codigo_descuento.email_enviado = True
                codigo_descuento.save()

                emails_enviados += 1
                self.stdout.write(
                    f'  ✓ Email enviado a {usuario.profile.instagram_account} ({usuario.email})'
                )

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error con {usuario.email}: {str(e)}')
                )

        # Resumen final
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'DRY-RUN completado. {usuarios_inactivos.count()} usuarios recibirían códigos.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Comando completado: {emails_enviados} emails enviados, {errores} errores')
            )