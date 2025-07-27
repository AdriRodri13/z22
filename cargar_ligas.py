import django
import difflib
import re
import os

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'z22.settings')
django.setup()

from home.models import Temporada, Liga, Equipo, Equipacion
from django.core.files import File

# Rutas base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_EQUIPOS = os.path.join(BASE_DIR, 'Equipos')
CARPETA_EQUIPACIONES = os.path.join(CARPETA_EQUIPOS, 'Equipaciones')

# Temporada fija
NOMBRE_TEMPORADA = '25-26'

# Info de ligas: nombre, logo, carpeta equipos, carpeta equipaciones
ligas_info = [
    {
        "nombre": "Bundesliga", 
        "logo": "bundes.png", 
        "carpeta": "Bundesliga",
        "carpeta_equipaciones": "Bundesliga"
    },
    {
        "nombre": "La Liga", 
        "logo": "LaLiga.png", 
        "carpeta": "Liga Española",
        "carpeta_equipaciones": "La Liga"
    },
    {
        "nombre": "Serie A", 
        "logo": "seria.png", 
        "carpeta": "Liga Italiana",
        "carpeta_equipaciones": "Serie A"
    },
    {
        "nombre": "Ligue 1", 
        "logo": "ligueone.png", 
        "carpeta": "Ligue One",
        "carpeta_equipaciones": "Ligue 1"
    },
    {
        "nombre": "Premier League", 
        "logo": "Premier.png", 
        "carpeta": "Premier League",
        "carpeta_equipaciones": "Premier League"
    },
]

# Diccionario de mapeo para nombres conocidos problemáticos
MAPEO_NOMBRES = {
    # === SERIE A (LIGA ITALIANA) ===
    "atalanta": "Atalanta",
    "bologna": "Bologna", 
    "cagliari": "Cagliari",
    "como": "Como",
    "cremonese": "Cremonese",
    "fiorentina": "Fiorentina",
    "genoa": "Genoa",
    "hellasverona": "Hellas Verona",
    "verona": "Hellas Verona",
    "inter": "Inter",
    "intermilan": "Inter",
    "juventus": "Juventus",
    "juve": "Juventus",
    "lazio": "Lazio",
    "lecce": "Lecce",
    "milan": "Milan",
    "acmilan": "Milan",
    "napoli": "Napoli",
    "parma": "Parma",
    "pisa": "Pisa",
    "roma": "Roma",
    "asroma": "Roma",
    "sassuolo": "Sassuolo",
    "torino": "Torino",
    "udinese": "Udinese",
    "venezia": "Venezia",
    "empoli": "Empoli",
    "monza": "Monza",
    
    # === LIGUE 1 ===
    "angers": "Angers",
    "auxerre": "Auxerre",
    "havre": "Le Havre",
    "lille": "Lille",
    "lorient": "Lorient",
    "metz": "Metz",
    "monaco": "Monaco",
    "nantes": "Nantes",
    "niza": "Nice",
    "nice": "Nice",
    "olimpiquemarsella": "Olympique Marseille",
    "marseille": "Olympique Marseille",
    "olimpiquelyon": "Olympique Lyon",
    "lyon": "Olympique Lyon",
    "psg": "Paris Saint-Germain",
    "parissaintgermain": "Paris Saint-Germain",
    "racingestrasburgo": "Racing Strasbourg",
    "strasbourg": "Racing Strasbourg",
    "racinglens": "Racing Lens",
    "lens": "Racing Lens",
    "rennais": "Rennes",
    "stadelederetois": "Stade de Reims",
    "reims": "Stade de Reims",
    "toulouse": "Toulouse",
    "brest": "Brest",
    "montpellier": "Montpellier",
    
    # === PREMIER LEAGUE ===
    "arsenal": "Arsenal",
    "astonvilla": "Aston Villa",
    "bournemouth": "Bournemouth",
    "brentford": "Brentford",
    "brighton": "Brighton",
    "burnley": "Burnley",
    "chelsea": "Chelsea",
    "crystalpalace": "Crystal Palace",
    "everton": "Everton",
    "fulham": "Fulham",
    "leeds": "Leeds United",
    "leicester": "Leicester City",
    "liverpool": "Liverpool",
    "manchestercity": "Manchester City",
    "mancity": "Manchester City",
    "manchesterunited": "Manchester United",
    "manunited": "Manchester United",
    "newcastle": "Newcastle United",
    "nottinghamforest": "Nottingham Forest",
    "southampton": "Southampton",
    "tottenham": "Tottenham Hotspur",
    "spurs": "Tottenham Hotspur",
    "westham": "West Ham United",
    "wolves": "Wolverhampton Wanderers",
    "ipswich": "Ipswich Town",
    
    # === LA LIGA (LIGA ESPAÑOLA) ===
    "alaves": "Deportivo Alavés",
    "athletic": "Athletic Bilbao",
    "bilbao": "Athletic Bilbao",
    "atleticomadrid": "Atlético Madrid",
    "atletico": "Atlético Madrid",
    "barcelona": "FC Barcelona",
    "barca": "FC Barcelona",
    "betis": "Real Betis",
    "realbetis": "Real Betis",
    "celta": "Celta Vigo",
    "celtavigo": "Celta Vigo",
    "elche": "Elche",
    "espanyol": "Espanyol",
    "getafe": "Getafe",
    "girona": "Girona",
    "laspalmas": "Las Palmas",
    "leganes": "Leganés",
    "levante": "Levante",
    "mallorca": "Mallorca",
    "osasuna": "Osasuna",
    "rayovallecano": "Rayo Vallecano",
    "rayo": "Rayo Vallecano",
    "realmadrid": "Real Madrid",
    "madrid": "Real Madrid",
    "realviedo": "Real Oviedo",
    "realsociedad": "Real Sociedad",
    "sociedad": "Real Sociedad",
    "sevilla": "Sevilla",
    "valencia": "Valencia",
    "valladolid": "Valladolid",
    "villarreal": "Villarreal",
    
    # === BUNDESLIGA ===
    "augsburgo": "FC Augsburg",
    "augsburg": "FC Augsburg",
    "bayerleverkusen": "Bayer Leverkusen",
    "leverkusen": "Bayer Leverkusen",
    "bayernmunich": "Bayern Munich",
    "bayern": "Bayern Munich",
    "bayernmunchen": "Bayern Munich",
    "bmonchengladbach": "Borussia Mönchengladbach",
    "gladbach": "Borussia Mönchengladbach",
    "borussiadortmund": "Borussia Dortmund",
    "dortmund": "Borussia Dortmund",
    "bvb": "Borussia Dortmund",
    "eintrachtfrankfurt": "Eintracht Frankfurt",
    "frankfurt": "Eintracht Frankfurt",
    "freiburg": "SC Freiburg",
    "hamburgo": "Hamburger SV",
    "hamburg": "Hamburger SV",
    "heidenheim": "FC Heidenheim",
    "hoffenheim": "TSG Hoffenheim",
    "koln": "FC Köln",
    "cologne": "FC Köln",
    "mainz05": "Mainz 05",
    "mainz": "Mainz 05",
    "rbleipzig": "RB Leipzig",
    "leipzig": "RB Leipzig",
    "stpauli": "FC St. Pauli",
    "stuttgart": "VfB Stuttgart",
    "unionberlin": "Union Berlin",
    "werderbremen": "Werder Bremen",
    "bremen": "Werder Bremen",
    "wolfsburg": "VfL Wolfsburg",
    "bochum": "VfL Bochum",
    "kiel": "Holstein Kiel",
}

def normalizar_nombre(nombre):
    """Normaliza nombres para comparación: minúsculas, sin espacios, sin caracteres especiales"""
    # Eliminar extensiones de archivo
    nombre = re.sub(r'\.(png|jpg|jpeg)$', '', nombre, flags=re.IGNORECASE)
    # Convertir a minúsculas y eliminar caracteres especiales
    nombre = re.sub(r'[^a-zA-Z0-9]', '', nombre.lower())
    return nombre

def buscar_equipo_existente(nombre_carpeta, equipos_liga):
    """
    Busca si ya existe un equipo que corresponda al nombre de la carpeta
    Usa mapeo personalizado y comparación difusa
    """
    nombre_normalizado = normalizar_nombre(nombre_carpeta)
    
    # 1. Buscar en mapeo personalizado
    if nombre_normalizado in MAPEO_NOMBRES:
        nombre_oficial = MAPEO_NOMBRES[nombre_normalizado]
        equipo_existente = equipos_liga.filter(nombre__iexact=nombre_oficial).first()
        if equipo_existente:
            return equipo_existente, nombre_oficial
    
    # 2. Buscar coincidencia exacta normalizada
    for equipo in equipos_liga:
        if normalizar_nombre(equipo.nombre) == nombre_normalizado:
            return equipo, equipo.nombre
    
    # 3. Buscar con difflib (comparación difusa)
    nombres_equipos = {normalizar_nombre(eq.nombre): eq.nombre for eq in equipos_liga}
    coincidencias = difflib.get_close_matches(
        nombre_normalizado, 
        nombres_equipos.keys(), 
        n=1, 
        cutoff=0.8  # Aumentar cutoff para ser más estricto
    )
    
    if coincidencias:
        nombre_coincidente = nombres_equipos[coincidencias[0]]
        equipo_existente = equipos_liga.filter(nombre__iexact=nombre_coincidente).first()
        if equipo_existente:
            return equipo_existente, nombre_coincidente
    
    # 4. No encontrado - devolver None para crear nuevo
    return None, nombre_carpeta

def buscar_logo_equipo(nombre_equipo, carpeta_liga):
    """Busca el archivo de logo que corresponde al nombre del equipo"""
    if not os.path.isdir(carpeta_liga):
        return None
    
    nombre_normalizado = normalizar_nombre(nombre_equipo)
    
    for archivo in os.listdir(carpeta_liga):
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            nombre_archivo_norm = normalizar_nombre(archivo)
            
            # Coincidencia exacta
            if nombre_archivo_norm == nombre_normalizado:
                return os.path.join(carpeta_liga, archivo)
            
            # Coincidencia parcial (uno contiene al otro)
            if (nombre_archivo_norm in nombre_normalizado or 
                nombre_normalizado in nombre_archivo_norm):
                return os.path.join(carpeta_liga, archivo)
    
    # Buscar con difflib
    archivos_norm = {normalizar_nombre(f): f for f in os.listdir(carpeta_liga) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))}
    
    coincidencias = difflib.get_close_matches(nombre_normalizado, archivos_norm.keys(), n=1, cutoff=0.7)
    if coincidencias:
        archivo_encontrado = archivos_norm[coincidencias[0]]
        return os.path.join(carpeta_liga, archivo_encontrado)
    
    return None

def verificar_estructura_archivos():
    """Verifica qué carpetas existen realmente"""
    print("🔍 Verificando estructura de archivos...")
    
    if os.path.exists(CARPETA_EQUIPACIONES):
        print(f"📁 Carpeta equipaciones encontrada: {CARPETA_EQUIPACIONES}")
        for item in os.listdir(CARPETA_EQUIPACIONES):
            item_path = os.path.join(CARPETA_EQUIPACIONES, item)
            if os.path.isdir(item_path):
                print(f"   📂 {item}")
    else:
        print(f"❌ Carpeta equipaciones no encontrada: {CARPETA_EQUIPACIONES}")
    
    if os.path.exists(CARPETA_EQUIPOS):
        print(f"📁 Carpeta equipos encontrada: {CARPETA_EQUIPOS}")
        for item in os.listdir(CARPETA_EQUIPOS):
            item_path = os.path.join(CARPETA_EQUIPOS, item)
            if os.path.isdir(item_path):
                print(f"   📂 {item}")
    else:
        print(f"❌ Carpeta equipos no encontrada: {CARPETA_EQUIPOS}")

def cargar_datos():
    # Verificar estructura primero
    verificar_estructura_archivos()
    
    # Crear temporada
    temporada, created = Temporada.objects.get_or_create(nombre=NOMBRE_TEMPORADA)
    print(f"\n{'✔' if created else 'ℹ'} Temporada '{temporada.nombre}' {'creada' if created else 'ya existe'}.\n")

    for liga_data in ligas_info:
        nombre_liga = liga_data["nombre"]
        logo_path = os.path.join(CARPETA_EQUIPOS, liga_data["logo"])
        carpeta_liga = os.path.join(CARPETA_EQUIPOS, liga_data["carpeta"])
        carpeta_equipaciones = os.path.join(CARPETA_EQUIPACIONES, liga_data["carpeta_equipaciones"])

        print(f"\n🏆 Procesando liga: {nombre_liga}")
        print(f"   📁 Carpeta equipos: {carpeta_liga}")
        print(f"   📁 Carpeta equipaciones: {carpeta_equipaciones}")
        
        # Verificar si las carpetas existen
        carpeta_liga_existe = os.path.isdir(carpeta_liga)
        carpeta_equipaciones_existe = os.path.isdir(carpeta_equipaciones)
        
        print(f"   ✓ Carpeta equipos existe: {carpeta_liga_existe}")
        print(f"   ✓ Carpeta equipaciones existe: {carpeta_equipaciones_existe}")
        
        if not carpeta_liga_existe and not carpeta_equipaciones_existe:
            print(f"   ⚠️ Saltando {nombre_liga} - No se encontraron carpetas")
            continue

        # Crear liga
        liga, created = Liga.objects.get_or_create(nombre=nombre_liga, temporada=temporada)
        
        if created and os.path.isfile(logo_path):
            with open(logo_path, 'rb') as lf:
                liga.logo.save(os.path.basename(logo_path), File(lf), save=True)
            print(f"✔ Liga '{nombre_liga}' creada con logo.")
        elif not created:
            print(f"ℹ Liga '{nombre_liga}' ya existía.")
        else:
            print(f"⚠ Liga '{nombre_liga}' creada sin logo (archivo no encontrado: {logo_path}).")

        equipos_procesados = set()  # Para evitar duplicados en esta ejecución

        # FASE 1: Crear equipos desde carpetas de equipaciones (prioridad)
        if carpeta_equipaciones_existe:
            print(f"\n📂 Procesando equipaciones en: {carpeta_equipaciones}")
            
            carpetas_equipaciones = [d for d in os.listdir(carpeta_equipaciones) 
                                   if os.path.isdir(os.path.join(carpeta_equipaciones, d))]
            print(f"   📋 Carpetas de equipos encontradas: {len(carpetas_equipaciones)}")
            
            for carpeta_equipo in carpetas_equipaciones:
                carpeta_equipo_path = os.path.join(carpeta_equipaciones, carpeta_equipo)
                print(f"   🔄 Procesando: {carpeta_equipo}")

                # Buscar si ya existe un equipo para esta carpeta
                equipos_liga = Equipo.objects.filter(liga=liga)
                equipo_existente, nombre_final = buscar_equipo_existente(carpeta_equipo, equipos_liga)

                if equipo_existente:
                    print(f"      ℹ Equipo encontrado: '{carpeta_equipo}' → '{equipo_existente.nombre}'")
                    equipo = equipo_existente
                else:
                    # Crear nuevo equipo
                    equipo = Equipo(nombre=nombre_final, liga=liga)
                    
                    # Buscar y asignar logo
                    logo_path = buscar_logo_equipo(nombre_final, carpeta_liga)
                    if logo_path and os.path.isfile(logo_path):
                        with open(logo_path, 'rb') as ef:
                            equipo.logo.save(os.path.basename(logo_path), File(ef), save=False)
                        print(f"      🆕 Equipo '{nombre_final}' creado con logo: {os.path.basename(logo_path)}")
                    else:
                        print(f"      🆕 Equipo '{nombre_final}' creado sin logo")
                    
                    equipo.save()

                equipos_procesados.add(normalizar_nombre(equipo.nombre))

                # Procesar equipaciones para este equipo
                equipaciones_añadidas = 0
                archivos_equipaciones = [f for f in os.listdir(carpeta_equipo_path) 
                                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                print(f"      📸 Imágenes encontradas: {len(archivos_equipaciones)}")
                
                for img in archivos_equipaciones:
                    ruta_img = os.path.join(carpeta_equipo_path, img)

                    # Verificar si ya existe esta equipación
                    if Equipacion.objects.filter(
                        equipo=equipo, 
                        temporada=temporada, 
                        imagen__icontains=img
                    ).exists():
                        continue

                    # Crear equipación
                    try:
                        with open(ruta_img, 'rb') as fimg:
                            equipacion = Equipacion(equipo=equipo, temporada=temporada)
                            equipacion.imagen.save(img, File(fimg), save=True)
                            equipaciones_añadidas += 1
                    except Exception as e:
                        print(f"      ❌ Error al procesar {img}: {e}")

                if equipaciones_añadidas > 0:
                    print(f"      ✔ {equipaciones_añadidas} equipación(es) añadida(s)")
                else:
                    print(f"      ℹ No se añadieron nuevas equipaciones")

        # FASE 2: Crear equipos desde logos que no fueron procesados
        if carpeta_liga_existe:
            print(f"\n🖼️ Procesando logos de equipos en: {carpeta_liga}")
            
            archivos_logos = [f for f in os.listdir(carpeta_liga) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            print(f"   📋 Logos encontrados: {len(archivos_logos)}")
            
            for archivo in archivos_logos:
                nombre_desde_archivo = os.path.splitext(archivo)[0].replace('_', ' ')
                nombre_normalizado = normalizar_nombre(nombre_desde_archivo)
                
                # Saltar si ya procesamos este equipo
                if nombre_normalizado in equipos_procesados:
                    continue
                
                # Verificar si ya existe
                equipos_liga = Equipo.objects.filter(liga=liga)
                equipo_existente, _ = buscar_equipo_existente(nombre_desde_archivo, equipos_liga)
                
                if not equipo_existente:
                    # Crear equipo desde logo
                    ruta_logo = os.path.join(carpeta_liga, archivo)
                    with open(ruta_logo, 'rb') as ef:
                        equipo = Equipo(nombre=nombre_desde_archivo, liga=liga)
                        equipo.logo.save(archivo, File(ef), save=True)
                        print(f"   🖼️ Equipo '{nombre_desde_archivo}' creado solo desde logo.")
                        equipos_procesados.add(nombre_normalizado)

        total_equipos = Equipo.objects.filter(liga=liga).count()
        total_equipaciones = Equipacion.objects.filter(equipo__liga=liga, temporada=temporada).count()
        print(f"\n✅ Liga '{nombre_liga}' completada.")
        print(f"   📊 Equipos: {total_equipos}")
        print(f"   📊 Equipaciones: {total_equipaciones}")

def mostrar_resumen():
    """Muestra un resumen de los datos cargados"""
    temporada = Temporada.objects.get(nombre=NOMBRE_TEMPORADA)
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN FINAL - Temporada {temporada.nombre}")
    print(f"{'='*60}")
    
    total_equipos_global = 0
    total_equipaciones_global = 0
    
    for liga in Liga.objects.filter(temporada=temporada):
        equipos = Equipo.objects.filter(liga=liga)
        total_equipaciones = Equipacion.objects.filter(equipo__liga=liga, temporada=temporada).count()
        
        total_equipos_global += equipos.count()
        total_equipaciones_global += total_equipaciones
        
        print(f"\n🏆 {liga.nombre}")
        print(f"   📋 Equipos: {equipos.count()}")
        print(f"   👕 Equipaciones: {total_equipaciones}")
        
        # Mostrar equipos sin logo
        sin_logo = equipos.filter(logo='').count()
        if sin_logo > 0:
            print(f"   ⚠️  Sin logo: {sin_logo}")
        
        # Mostrar equipos sin equipaciones
        sin_equipaciones = equipos.filter(equipaciones__isnull=True).count()
        if sin_equipaciones > 0:
            print(f"   ⚠️  Sin equipaciones: {sin_equipaciones}")
            
        # Mostrar algunos equipos como ejemplo
        if equipos.exists():
            ejemplos = equipos[:3]
            print(f"   📝 Ejemplos: {', '.join([eq.nombre for eq in ejemplos])}")
    
    print(f"\n{'='*60}")
    print(f"🎯 TOTALES GLOBALES:")
    print(f"   📋 Total equipos: {total_equipos_global}")
    print(f"   👕 Total equipaciones: {total_equipaciones_global}")
    print(f"{'='*60}")
    
if __name__ == '__main__':
    print("🚀 Iniciando carga de datos de fútbol...")
    print("📊 Script mejorado para todas las ligas")
    cargar_datos()
    mostrar_resumen()
    print(f"\n🎉 ¡Proceso completado!")