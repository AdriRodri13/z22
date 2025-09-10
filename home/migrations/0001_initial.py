# Generated manually for data transition
import django.core.files.storage
import django.db.models.deletion
from django.db import migrations, models


def migrate_data_forward(apps, schema_editor):
    """Migrar datos de la estructura antigua a la nueva"""
    from django.db import connection
    
    cursor = connection.cursor()
    
    # 1. Crear sección "Fútbol"
    cursor.execute("""
        INSERT INTO home_seccion (nombre, descripcion, icono, orden, activa, creado_en)
        VALUES ('Fútbol', 'Sección de fútbol con todas las ligas y equipos', 'fas fa-futbol', 1, true, NOW())
    """)
    
    # Obtener el ID de la sección creada
    cursor.execute("SELECT id FROM home_seccion WHERE nombre = 'Fútbol'")
    seccion_futbol_id = cursor.fetchone()[0]
    
    # 2. Migrar ligas como subsecciones
    cursor.execute("""
        INSERT INTO home_subseccion (nombre, logo, descripcion, orden, activa, creado_en, seccion_id)
        SELECT nombre, logo, descripcion, orden, activa, creado_en, %s
        FROM home_liga
        ORDER BY id
    """, [seccion_futbol_id])
    
    # 3. Migrar equipos como subsubsecciones
    cursor.execute("""
        INSERT INTO home_subsubseccion (nombre, logo, descripcion, orden, activa, creado_en, subseccion_id)
        SELECT 
            e.nombre, 
            e.logo, 
            e.descripcion, 
            e.orden, 
            e.activa, 
            e.creado_en,
            sub.id
        FROM home_equipo e
        INNER JOIN home_liga l ON e.liga_id = l.id
        INNER JOIN home_subseccion sub ON sub.nombre = l.nombre
        ORDER BY e.id
    """)
    
    # 4. Migrar equipaciones como prendas
    cursor.execute("""
        INSERT INTO home_prenda (nombre, imagen, descripcion, precio, disponible, orden, creado_en, subsubseccion_id)
        SELECT 
            eq.nombre,
            eq.imagen,
            eq.descripcion,
            eq.precio,
            eq.disponible,
            eq.orden,
            eq.creado_en,
            subsub.id
        FROM home_equipacion eq
        INNER JOIN home_equipo e ON eq.equipo_id = e.id
        INNER JOIN home_liga l ON e.liga_id = l.id
        INNER JOIN home_subseccion sub ON sub.nombre = l.nombre
        INNER JOIN home_subsubseccion subsub ON subsub.nombre = e.nombre AND subsub.subseccion_id = sub.id
        ORDER BY eq.id
    """)


def migrate_data_backward(apps, schema_editor):
    """Revertir la migración (no implementado por seguridad)"""
    pass


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # Crear las nuevas tablas
        migrations.CreateModel(
            name='Seccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('icono', models.CharField(blank=True, help_text='Clase CSS del icono (ej: fas fa-tshirt)', max_length=50, null=True)),
                ('orden', models.PositiveIntegerField(default=0, help_text='Orden de visualización')),
                ('activa', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Sección',
                'verbose_name_plural': 'Secciones',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Subseccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to='logos/subsecciones/')),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('activa', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('seccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subsecciones', to='home.seccion')),
            ],
            options={
                'verbose_name': 'Subsección',
                'verbose_name_plural': 'Subsecciones',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Subsubseccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to='logos/subsubsecciones/')),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('activa', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('subseccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subsubsecciones', to='home.subseccion')),
            ],
            options={
                'verbose_name': 'Subsubsección',
                'verbose_name_plural': 'Subsubsecciones',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Prenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, help_text='Nombre opcional de la prenda', max_length=100, null=True)),
                ('imagen', models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to='prendas/')),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('disponible', models.BooleanField(default=True)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('subsubseccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prendas', to='home.subsubseccion')),
            ],
            options={
                'verbose_name': 'Prenda',
                'verbose_name_plural': 'Prendas',
                'ordering': ['orden', '-creado_en'],
            },
        ),
        
        # Migrar los datos
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]