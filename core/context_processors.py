from django.conf import settings
from django.http import HttpRequest


def csp_nonce(request: HttpRequest) -> dict[str, str]:
    """Expone el nonce CSP generado por petición a las plantillas."""
    return {
        'csp_nonce': getattr(request, 'csp_nonce', ''),
    }


def site_features(request: HttpRequest) -> dict[str, object]:
    """Expone las banderas de funcionalidades y datos de contacto del sitio a las plantillas."""
    return {
        'private_classes_enabled': bool(getattr(settings, 'PRIVATE_CLASSES_ENABLED', True)),
        'contact_email': getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', 'contacto@adrigalvez.com'),
    }
