from django.http import HttpRequest


def csp_nonce(request: HttpRequest) -> dict[str, str]:
    """Expone el nonce CSP generado por petición a las plantillas."""
    return {
        'csp_nonce': getattr(request, 'csp_nonce', ''),
    }
