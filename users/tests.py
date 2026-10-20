from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from users.models import UserProfile


@override_settings(
    ALLOWED_HOSTS=["adrianadmin.egalvez.es", "testserver"],
    ADMIN_HOSTS=["adrianadmin.egalvez.es"],
)
class EmailAuthAndProfileTestCase(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_superuser(
            username="adrian_admin",
            email="admin@adrigalvez.com",
            password="StrongPassword123!",
        )

    def test_profile_created_automatically(self):
        """Verifica que el UserProfile se cree automáticamente al crear un User."""
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_login_with_email_succeeds(self):
        """Verifica que el usuario pueda iniciar sesión usando su correo electrónico."""
        response = self.client.post(
            "/login/",
            data={"username": "ADMIN@adrigalvez.com", "password": "StrongPassword123!"},
            HTTP_HOST="adrianadmin.egalvez.es",
        )
        self.assertEqual(response.status_code, 302)

    def test_login_with_username_fails(self):
        """Verifica que ya no se pueda iniciar sesión usando el username sino solo con el email."""
        response = self.client.post(
            "/login/",
            data={"username": "adrian_admin", "password": "StrongPassword123!"},
            HTTP_HOST="adrianadmin.egalvez.es",
        )
        # Devuelve 200 con formulario de error (no redirige)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Correo electrónico")
