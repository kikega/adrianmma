from django.db import models
from django.utils import timezone


class FighterProfile(models.Model):
    """
    Modelo que representa el perfil del luchador.
    Almacena información personal, biografía, y estadísticas de contacto.
    """
    name = models.CharField(max_length=200, default="Adrián Gálvez")
    nickname = models.CharField(max_length=100, default="The Butcher")
    bio = models.TextField(blank=True)
    specialties = models.CharField(max_length=500, blank=True)
    achievements = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to='fighter/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil del Luchador"
        verbose_name_plural = "Perfiles"

    def __str__(self) -> str:
        return f"{self.name} '{self.nickname}'"


class Service(models.Model):
    """
    Modelo que representa un servicio o clase impartida por el luchador.
    """
    SERVICE_TYPES = [
        ('defensa_personal', 'Defensa Personal'),
        ('jiujitsu', 'Jiu-Jitsu'),
        ('boxeo', 'Boxeo'),
        ('mma', 'MMA'),
    ]
    
    name = models.CharField(max_length=100, choices=SERVICE_TYPES)
    description = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['order']

    def __str__(self) -> str:
        return str(self.get_name_display())


class Multimedia(models.Model):
    """
    Modelo para la gestión de galería multimedia (fotos y vídeos).
    """
    MEDIA_TYPES = [
        ('foto', 'Foto'),
        ('video', 'Video'),
    ]
    
    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    image = models.ImageField(upload_to='multimedia/photos/', blank=True)
    video_url = models.URLField(blank=True, help_text="URL de YouTube/Vimeo")
    video_file = models.FileField(upload_to='multimedia/videos/', blank=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Multimedia"
        verbose_name_plural = "Galería Multimedia"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return str(self.title)


class SocialNetwork(models.Model):
    """
    Modelo para gestionar los enlaces a las redes sociales del luchador.
    """
    PLATFORMS = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
    ]
    
    platform = models.CharField(max_length=50, choices=PLATFORMS)
    username = models.CharField(max_length=100)
    url = models.URLField()
    icon_class = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Red Social"
        verbose_name_plural = "Redes Sociales"
        ordering = ['order']

    def __str__(self) -> str:
        return f"{self.get_platform_display()}: @{self.username}"


class ContactMessage(models.Model):
    """
    Modelo para almacenar los mensajes recibidos desde el formulario de contacto de la web.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    service_type = models.CharField(max_length=50, choices=Service.SERVICE_TYPES, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y')}"