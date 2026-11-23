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
        from django.core.cache import cache
        cache.clear()
        self.client = Client()

        # Crear perfil del luchador
        self.fighter = FighterProfile.objects.create(
            name="Adrián Gálvez",
            nickname="The Butcher",
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

    def test_security_headers_and_csp_nonce_on_landing(self):
        """Verifica CSP con nonce válido, cabeceras de seguridad y ausencia de JS inline/CDN externo."""
        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)

        csp = response.headers.get('Content-Security-Policy', '')
        self.assertIn("script-src 'nonce-", csp)
        self.assertIn("'strict-dynamic'", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertIn("base-uri 'none'", csp)
        self.assertIn("frame-ancestors 'self'", csp)
        self.assertNotIn("'unsafe-inline'", csp.split("script-src")[1].split(";")[0])

        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIn('camera=()', response.headers.get('Permissions-Policy', ''))
        self.assertEqual(response.headers.get('Cross-Origin-Opener-Policy'), 'same-origin-allow-popups')

        html = response.content.decode('utf-8')
        self.assertNotIn('unpkg.com', html)
        self.assertNotIn('onclick=', html)
        self.assertNotIn('fa-boxing-glove', html)
        self.assertIn('Saltar al contenido principal', html)
        self.assertIn('role="tablist"', html)
        self.assertIn('action="/contacto/"', html)
        self.assertIn('method="post"', html)

    def test_contact_submission_non_htmx_html_fallback(self):
        """Verifica que el formulario funcione sin HTMX cuando el navegador solicita HTML."""
        payload = {
            'name': 'Laura Gómez',
            'email': 'laura@example.com',
            'phone': '',
            'service_type': 'boxeo',
            'message': 'Consulta sin JavaScript.',
            'website': '',
        }
        response = self.client.post(
            reverse('core:contact'),
            data=payload,
            HTTP_ACCEPT='text/html,application/xhtml+xml',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '¡Mensaje Enviado!')
        self.assertTrue(ContactMessage.objects.filter(email='laura@example.com').exists())

    def test_contact_validation_sets_aria_invalid_and_describedby(self):
        """Verifica atributos ARIA de accesibilidad en campos inválidos."""
        response = self.client.post(
            reverse('core:contact'),
            data={'name': '   ', 'email': 'mal', 'message': ''},
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, 'aria-invalid="true"', status_code=422)
        self.assertContains(response, 'aria-describedby="contact-name-error"', status_code=422)
        self.assertContains(response, 'aria-describedby="contact-email-error"', status_code=422)
        self.assertContains(response, 'aria-describedby="contact-message-error"', status_code=422)

    def test_contact_rate_limiting(self):
        """Verifica que tras superar el límite de envíos por IP responda con HTTP 429."""
        payload = {
            'name': 'Usuario Repetido',
            'email': 'repetido@example.com',
            'message': 'Mensaje de prueba',
            'website': '',
        }
        for _ in range(5):
            resp = self.client.post(reverse('core:contact'), data=payload, HTTP_HX_REQUEST='true')
            self.assertEqual(resp.status_code, 200)

        limited_resp = self.client.post(reverse('core:contact'), data=payload, HTTP_HX_REQUEST='true')
        self.assertEqual(limited_resp.status_code, 429)
        self.assertContains(limited_resp, 'Has enviado demasiados mensajes', status_code=429)

    def test_gallery_endpoint_handles_missing_image_and_video_file(self):
        """Verifica que la galería parcial no falle si falta imagen y soporte video_file."""
        Multimedia.objects.create(title="Foto sin archivo", media_type="foto")
        dummy_video = SimpleUploadedFile("clip.mp4", b"\x00\x00\x00\x20ftypmp42", content_type="video/mp4")
        Multimedia.objects.create(title="Video local", media_type="video", video_file=dummy_video)

        foto_resp = self.client.get(reverse('core:gallery'), {'type': 'foto'})
        self.assertEqual(foto_resp.status_code, 200)

        video_resp = self.client.get(reverse('core:gallery'), {'type': 'video'})
        self.assertEqual(video_resp.status_code, 200)
        self.assertContains(video_resp, 'clip')
        self.assertNotContains(video_resp, 'gallery-videos-combined')

    def test_get_client_ip_avoids_x_forwarded_for_spoofing(self):
        """Verifica que X-Real-IP o el último salto de X-Forwarded-For prevalezcan."""
        from django.test import RequestFactory
        from core.middleware import get_client_ip

        rf = RequestFactory()
        req = rf.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 198.51.100.2', HTTP_X_REAL_IP='198.51.100.2')
        self.assertEqual(get_client_ip(req), '198.51.100.2')

        req_no_real = rf.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 203.0.113.9')
        self.assertEqual(get_client_ip(req_no_real), '203.0.113.9')

    @override_settings(PRIVATE_CLASSES_ENABLED=True)
    def test_private_classes_enabled_reads_prices_from_db(self):
        """Cuando PRIVATE_CLASSES_ENABLED=True, muestra la sección y lee precios dinámicos de BBDD."""
        self.service1.price_per_hour = 42.50
        self.service1.save()

        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['private_classes_enabled'])
        self.assertContains(response, 'id="servicios"')
        self.assertContains(response, 'href="#servicios"')
        self.assertContains(response, 'id="contact-service"')
        self.assertContains(response, '42,50€')
        self.assertContains(response, '40€')

    @override_settings(PRIVATE_CLASSES_ENABLED=False)
    def test_private_classes_disabled_hides_section_links_and_service_field(self):
        """Cuando PRIVATE_CLASSES_ENABLED=False, oculta sección, enlaces y selector de clases."""
        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['private_classes_enabled'])
        self.assertEqual(list(response.context['services']), [])
        self.assertNotContains(response, 'id="servicios"')
        self.assertNotContains(response, 'href="#servicios"')
        self.assertNotContains(response, 'Ver Servicios')
        self.assertNotContains(response, 'Reservar Clase')
        self.assertNotContains(response, 'id="contact-service"')
        self.assertNotContains(response, '35€')

        # El fragmento HTMX del formulario tampoco debe incluir el selector de servicio
        form_response = self.client.get(reverse('core:contact_form'))
        self.assertEqual(form_response.status_code, 200)
        self.assertNotContains(form_response, 'id="contact-service"')

    @override_settings(PRIVATE_CLASSES_ENABLED=False)
    def test_contact_submission_ignores_service_type_when_private_classes_disabled(self):
        """Cuando PRIVATE_CLASSES_ENABLED=False, el contacto funciona e ignora service_type."""
        payload = {
            'name': 'Ana Torres',
            'email': 'ana@example.com',
            'phone': '',
            'service_type': 'mma',
            'message': 'Consulta general de colaboración.',
            'website': '',
        }
        response = self.client.post(
            reverse('core:contact'),
            data=payload,
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        saved = ContactMessage.objects.get(email='ana@example.com')
        self.assertEqual(saved.service_type, '')
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('Servicio de interés:', mail.outbox[0].body)


@override_settings(
    ALLOWED_HOSTS=['adrian.egalvez.es', 'adrianadmin.egalvez.es', 'testserver'],
    ADMIN_HOSTS=['adrianadmin.egalvez.es'],
)
class AdminSubdomainTestCase(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = Client()

    def test_admin_not_accessible_on_public_domain(self):
        """En el dominio público, /admin/ debe devolver 404 Not Found."""
        response = self.client.get('/admin/', HTTP_HOST='adrian.egalvez.es')
        self.assertEqual(response.status_code, 404)

    def test_admin_accessible_on_admin_subdomain(self):
        """En el subdominio de administración, la raíz / redirige al login del admin."""
        response = self.client.get('/', HTTP_HOST='adrianadmin.egalvez.es')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])
        self.assertEqual(response.headers.get('X-Robots-Tag'), 'noindex, nofollow')

    def test_admin_login_brute_force_protection(self):
        """Tras 5 intentos fallidos de login en el subdominio admin, bloquea con 403."""
        for _ in range(5):
            resp = self.client.post(
                '/login/',
                data={'username': 'admin', 'password': 'wrongpassword'},
                HTTP_HOST='adrianadmin.egalvez.es',
            )
            self.assertEqual(resp.status_code, 200)

        # El 6º intento debe ser rechazado con 403 Forbidden
        blocked_resp = self.client.post(
            '/login/',
            data={'username': 'admin', 'password': 'wrongpassword'},
            HTTP_HOST='adrianadmin.egalvez.es',
        )
        self.assertEqual(blocked_resp.status_code, 403)

