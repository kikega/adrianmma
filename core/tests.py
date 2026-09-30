import tempfile
import shutil
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import FighterProfile, Service, Multimedia, SocialNetwork, ContactMessage
from core.forms import ContactMessageForm
from core import services


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CoreViewsAndFormsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Crear perfil del luchador
        self.fighter = FighterProfile.objects.create(
            name="Adrián Gálvez",
            nickname="The Butcher",
            bio="Luchador profesional de MMA.",
            achievements="Campeón de España Amateur IMAF 2021",
            phone="+34 600 111 222",
            email="contacto@adrigalvez.com",
            location="Alicante - Climent Club",
            is_active=True,
        )

        # Crear servicios
        self.service1 = Service.objects.create(
            name="defensa_personal",
            description="Técnicas de protección y control",
            price_per_hour=35.00,
            order=1,
            is_active=True,
        )
        self.service2 = Service.objects.create(
            name="jiujitsu",
            description="Arte brasilero Gi & No-Gi",
            price_per_hour=40.00,
            order=2,
            is_active=True,
        )

        # Crear multimedia con imagen dummy
        dummy_image = SimpleUploadedFile("test_foto.jpg", b"\x00\x01\x02", content_type="image/jpeg")
        self.photo = Multimedia.objects.create(
            title="Entrenamiento en el Ring Test",
            media_type="foto",
            image=dummy_image,
            is_featured=True,
        )
        self.video = Multimedia.objects.create(
            title="Highlight de Combate Test",
            media_type="video",
            video_url="https://www.youtube.com/watch?v=test",
            is_featured=True,
        )

        # Crear red social
        self.social = SocialNetwork.objects.create(
            platform="instagram",
            username="adrigalvez17",
            url="https://instagram.com/adrigalvez17",
            icon_class="fab fa-instagram",
            order=1,
            is_active=True,
        )

    def test_landing_page_status_and_content(self):
        """Verifica que la landing cargue 200 OK y muestre datos dinámicos."""
        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ADRIÁN")
        self.assertContains(response, "The Butcher")
        self.assertContains(response, "Defensa Personal")
        self.assertContains(response, "35€")
        self.assertContains(response, "40€")
        self.assertContains(response, "https://instagram.com/adrigalvez17")
        self.assertIn('form', response.context)
        self.assertIn('services', response.context)
        self.assertIn('fighter', response.context)

    def test_contact_form_view_endpoint(self):
        """Verifica el endpoint GET para recargar el formulario con HTMX."""
        response = self.client.get(reverse('core:contact_form'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="contact-form-container"')
        self.assertContains(response, 'contact-name')

    def test_contact_submission_valid_htmx(self):
        """Verifica el envío exitoso de formulario a través de HTMX."""
        payload = {
            'name': 'Carlos Perez',
            'email': 'carlos@example.com',
            'phone': '+34 611 222 333',
            'service_type': 'mma',
            'message': 'Quiero información sobre clases particulares de MMA.',
            'website': '',  # Honeypot vacío
        }
        response = self.client.post(
            reverse('core:contact'),
            data=payload,
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '¡Mensaje Enviado!')
        self.assertTrue(ContactMessage.objects.filter(email='carlos@example.com').exists())

        # Verificar que se envió el email de aviso
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Carlos Perez', mail.outbox[0].subject)

    def test_contact_submission_honeypot_spam(self):
        """Verifica que si un bot rellena el campo trampa 'website', se rechace como spam."""
        payload = {
            'name': 'Spam Bot',
            'email': 'bot@spammer.com',
            'phone': '+12345678',
            'service_type': 'boxeo',
            'message': 'Compre criptomonedas ahora',
            'website': 'http://spam-link.com',  # Honeypot completado por bot
        }
        response = self.client.post(
            reverse('core:contact'),
            data=payload,
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 422)
        # No debe haberse guardado en base de datos
        self.assertFalse(ContactMessage.objects.filter(email='bot@spammer.com').exists())
        # No debe haberse enviado email
        self.assertEqual(len(mail.outbox), 0)

    def test_contact_submission_invalid_fields(self):
        """Verifica que campos vacíos o email inválido devuelvan errores."""
        payload = {
            'name': '',
            'email': 'email-invalido',
            'message': '',
        }
        response = self.client.post(
            reverse('core:contact'),
            data=payload,
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, 'El nombre es requerido', status_code=422)
        self.assertContains(response, 'Introduce una dirección de email válida', status_code=422)
        self.assertContains(response, 'El mensaje es requerido', status_code=422)

    def test_services_get_gallery_items_filter(self):
        """Verifica el filtrado correcto de items de galería por tipo."""
        photos = services.get_gallery_items('foto')
        self.assertTrue(photos.filter(title="Entrenamiento en el Ring Test").exists())

        videos = services.get_gallery_items('video')
        self.assertTrue(videos.filter(title="Highlight de Combate Test").exists())

        invalid = services.get_gallery_items('invalido')
        self.assertEqual(invalid.count(), 0)
