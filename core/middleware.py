import time
import logging
import traceback
from django.http import JsonResponse, HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('core')
request_logger = logging.getLogger('core.requests')


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

        # Obtener IP real considerando Nginx proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '-')

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
