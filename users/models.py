from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extiende el modelo de usuario nativo de Django con información adicional de perfil.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Usuario",
    )
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    role = models.CharField("Cargo / Rol", max_length=100, blank=True)
    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self) -> str:
        return f"Perfil de {self.user.email or self.user.username}"
