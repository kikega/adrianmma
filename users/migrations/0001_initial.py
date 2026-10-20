from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="Teléfono"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Cargo / Rol"
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Notas")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Última actualización"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to="auth.user",
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil de Usuario",
                "verbose_name_plural": "Perfiles de Usuario",
            },
        ),
    ]
