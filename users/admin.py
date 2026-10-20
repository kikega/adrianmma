from django import forms
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile


class EmailAdminAuthenticationForm(AdminAuthenticationForm):
    """
    Formulario de acceso al panel de administración que solicita el correo electrónico
    en lugar del nombre de usuario.
    """
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        "invalid_login": (
            "Por favor, introduce un correo electrónico y una contraseña correctos "
            "para una cuenta de personal. Ten en cuenta que ambos campos pueden "
            "distinguir entre mayúsculas y minúsculas."
        ),
    }


class CustomUserChangeForm(UserChangeForm):
    """Garantiza que el correo electrónico sea obligatorio y único al gestionar usuarios."""
    email = forms.EmailField(label="Correo electrónico", required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este correo electrónico.")
        return email


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Perfil Extendido"
    verbose_name_plural = "Perfil Extendido"
    fk_name = "user"


# Configurar el formulario de login del Admin para pedir Correo Electrónico
admin.site.login_form = EmailAdminAuthenticationForm

# Reemplazar el UserAdmin por defecto para mostrar el perfil extendido y priorizar el email
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    inlines = (UserProfileInline,)
    list_display = ("email", "username", "first_name", "last_name", "is_staff", "is_active")
    list_display_links = ("email", "username")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)
