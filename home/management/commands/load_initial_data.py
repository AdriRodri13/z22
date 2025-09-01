from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = "Carga los datos iniciales en la BBDD desde initial_data.json en la raíz del repo"

    def handle(self, *args, **options):
        fixture_path = os.path.join(os.getcwd(), "initial_data.json")

        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR("❌ No se encontró initial_data.json en la raíz del repo"))
            return

        self.stdout.write("📦 Cargando datos iniciales desde initial_data.json...")
        try:
            call_command("loaddata", fixture_path, verbosity=1)
            self.stdout.write(self.style.SUCCESS("✅ Datos iniciales cargados correctamente"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error cargando datos: {e}"))
