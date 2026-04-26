import logging
from django.http import JsonResponse, HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin
import traceback

logger = logging.getLogger('core')

class GlobalExceptionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para capturar excepciones globales no controladas,
    registrar el error detallado en los logs y retornar una respuesta unificada.
    """
    
    def process_exception(self, request, exception):
        # Log the detailed exception
        logger.error(
            f"Error no controlado en la petición: {request.method} {request.path}\n"
            f"Excepción: {str(exception)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # Determine the response format
        if hasattr(request, 'htmx') and request.htmx:
            # If HTMX, might return a snippet or a specific 500 error page template.
            # Returning a generic message to the frontend.
            return HttpResponseServerError("Ha ocurrido un error interno. Por favor, inténtelo de nuevo.")
        elif request.headers.get('accept', '').find('application/json') != -1:
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
        
        # Returning None means Django will handle the 500 error with its default template,
        # but the error is now safely logged.
        return None
