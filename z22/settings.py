from pathlib import Path
import os
import dj_database_url

# === BASE DIR ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === VARIABLES FIJAS PARA PRODUCCIÓN DESDE LOCAL ===
SECRET_KEY = "clave_segura"
DEBUG = False
ALLOWED_HOSTS = ["web-production-f968.up.railway.app", "www.web-production-f968.up.railway.app"]

DATABASES = {
    'default': dj_database_url.config(default="postgresql://postgres:bGFsLExHFpqITDgROTJgUNZzylyVULFq@interchange.proxy.rlwy.net:28561/railway")
}

CLOUDINARY_CLOUD_NAME = "dwl0lbes7"
CLOUDINARY_API_KEY = "227498335462626"
CLOUDINARY_API_SECRET = "L9wZH_YO0j9XB-v1BfRtFMHp2cw"

# === APPS ===
APPS_PROPIAS = [
    'home',
    'panel_admin',
]

APPS_TERCEROS = [
    'cloudinary',
    'cloudinary_storage',
    'whitenoise.runserver_nostatic',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + APPS_PROPIAS + APPS_TERCEROS

# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === GENERAL ===
ROOT_URLCONF = 'z22.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'z22.wsgi.application'

# === PASSWORD VALIDATORS ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === LOCALIZACIÓN ===
LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

# === STATIC FILES ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# === MEDIA ===
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
}
if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    raise Exception("❌ Cloudinary no está configurado correctamente. Revisa tus claves.")

# === FINAL ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
