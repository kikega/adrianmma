import time
import secrets
import logging
import traceback
from django.conf import settings
from django.core.cache import cache
from django.http import Http404, JsonResponse, HttpResponseServerError, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('core')
request_logger = logging.getLogger('core.requests')
security_logger = logging.getLogger('django.security')


def get_client_ip(request):
    """
    Obtiene la IP del cliente detrás de Nginx priorizando X-Real-IP
    (establecida directamente por el proxy) o el último salto de X-Forwarded-For,
    evitando falsificación mediante cabeceras X-Forwarded-For enviadas por el cliente.
    """
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR', '-')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Genera un nonce criptográfico por petición y añade cabeceras de seguridad
    modernas (CSP, Referrer-Policy, Permissions-Policy, COOP, nosniff).
    """

    def process_request(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)

    def process_response(self, request, response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault(
            'Permissions-Policy',
            'camera=(), geolocation=(), microphone=(), focus-without-user-activation=()',
        )
        response.headers.setdefault('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')

        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type and 'Content-Security-Policy' not in response.headers:
            if getattr(request, 'urlconf', None) == 'adrian.urls_admin':
                # Política base compatible con los scripts inline propios de Django Admin
                response.headers['Content-Security-Policy'] = (
                    "object-src 'none'; base-uri 'self'; frame-ancestors 'self'"
                )
            else:
                nonce = getattr(request, 'csp_nonce', '')
                csp_directives = [
                    "default-src 'self'",
                    f"script-src 'nonce-{nonce}' 'strict-dynamic' 'report-sample'",
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
                    "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
                    "img-src 'self' data: https:",
                    "media-src 'self'",
                    "frame-src https://maps.google.com https://www.google.com https://www.youtube.com https://www.youtube-nocookie.com https://player.vimeo.com",
                    "connect-src 'self'",
                    "object-src 'none'",
                    "base-uri 'none'",
                    "form-action 'self'",
                    "frame-ancestors 'self'",
                ]
                response.headers['Content-Security-Policy'] = '; '.join(csp_directives)

        return response


class AdminSubdomainMiddleware(MiddlewareMixin):
    """
    Enruta las peticiones dirigidas al subdominio de administración hacia `adrian.urls_admin`
    y aplica protección contra fuerza bruta en el inicio de sesión del panel.
    """
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_SECONDS = 600  # 10 minutos

    def process_request(self, request):
        host = request.get_host().split(':')[0].lower()
        admin_hosts = [h.lower() for h in getattr(settings, 'ADMIN_HOSTS', [])]

        if host in admin_hosts:
            request.urlconf = 'adrian.urls_admin'

            # Protección contra fuerza bruta en el login del admin
            if request.method == 'POST' and request.path == '/login/':
                ip = get_client_ip(request)
                cache_key = f"admin_login_attempts_{ip}"
                attempts = cache.get(cache_key, 0)
                if attempts >= self.MAX_LOGIN_ATTEMPTS:
                    security_logger.warning(
                        f"Bloqueo por fuerza bruta en Admin Login desde IP: {ip} (Host: {host})"
                    )
                    return HttpResponseForbidden(
                        "Demasiados intentos fallidos. Por favor, espera 10 minutos antes de volver a intentarlo."
                    )

    def process_response(self, request, response):
        if getattr(request, 'urlconf', None) == 'adrian.urls_admin':
            # Evitar que buscadores indexen cualquier página del subdominio de administración
            response.headers['X-Robots-Tag'] = 'noindex, nofollow'

            # Contabilizar o limpiar intentos de login según resultado
            if request.method == 'POST' and request.path == '/login/':
                ip = get_client_ip(request)
                cache_key = f"admin_login_attempts_{ip}"
                # En Django Admin, un login exitoso redirige (302); un fallo devuelve 200 con el formulario
                if response.status_code == 200:
                    attempts = cache.get(cache_key, 0) + 1
                    cache.set(cache_key, attempts, self.LOCKOUT_SECONDS)
                    security_logger.warning(
                        f"Intento de login fallido ({attempts}/{self.MAX_LOGIN_ATTEMPTS}) en Admin desde IP: {ip}"
                    )
                elif response.status_code in (301, 302):
                    cache.delete(cache_key)

        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar cada petición HTTP recibida:
    Método, ruta, IP remota, código de estado HTTP y tiempo de ejecución.
    """
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        duration = 0
        if hasattr(request, '_start_time'):
            duration = (time.time() - request._start_time) * 1000  # ms

        ip = get_client_ip(request)

        status_code = getattr(response, 'status_code', '-')
        msg = f"{request.method} {request.get_full_path()} - {status_code} ({duration:.2f}ms) IP: {ip}"

        if isinstance(status_code, int) and status_code >= 400:
            request_logger.warning(msg)
        else:
            request_logger.info(msg)

        return response


class GlobalExceptionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para capturar excepciones globales no controladas,
    registrar el error detallado en los logs con traceback y retornar una respuesta segura.
    """
    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return None

        logger.error(
            f"Error no controlado en la petición: {request.method} {request.path}\n"
            f"Excepción: {str(exception)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        if hasattr(request, 'htmx') and request.htmx:
            return HttpResponseServerError("Ha ocurrido un error interno. Por favor, inténtelo de nuevo.")
        elif request.headers.get('accept', '').find('application/json') != -1:
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
        
        return None
