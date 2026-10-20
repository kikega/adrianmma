from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """
    Backend de autenticación que permite iniciar sesión utilizando el correo electrónico
    (insensible a mayúsculas/minúsculas).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email") or username
        if not email or not password:
            return None

        email = email.strip()
        # Buscar usuario por email (case-insensitive)
        user = UserModel.objects.filter(email__iexact=email).order_by("id").first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
