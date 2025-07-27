from django.conf import settings
from django.core.files.storage import FileSystemStorage

def seleccionar_storage():
    if settings.DEBUG:
        return FileSystemStorage()
    else:
        # Solo importar Cloudinary en producción
        from cloudinary_storage.storage import MediaCloudinaryStorage
        return MediaCloudinaryStorage()