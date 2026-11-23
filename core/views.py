from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.cache import cache
from django.utils import timezone

from . import services
from .middleware import get_client_ip
from .models import FighterProfile, Multimedia

ALLOWED_MEDIA_TYPES = {'foto', 'video'}
CONTACT_RATE_LIMIT = 5
CONTACT_RATE_WINDOW_SECONDS = 600


def _build_landing_context(form=None, contact_submitted=False):
    return {
        'fighter': services.get_active_fighter(),
        'services': services.get_active_services(),
        'photos': list(services.get_gallery_items('foto', limit=12)),
        'videos': services.get_gallery_items('video', limit=6),
        'social_networks': services.get_active_social_networks(),
        'form': form if form is not None else services.get_contact_form(),
        'contact_submitted': contact_submitted,
    }


def landing(request: HttpRequest) -> HttpResponse:
    return render(request, 'core/landing.html', _build_landing_context())


@require_GET
def sitemap_xml(request: HttpRequest) -> HttpResponse:
    """
    Genera sitemap.xml con fecha lastmod dinámica basada en la última
    actualización del perfil o de la galería multimedia.
    """
    candidates = []
    latest_fighter = FighterProfile.objects.filter(is_active=True).order_by('-updated_at').first()
    if latest_fighter and latest_fighter.updated_at:
        candidates.append(latest_fighter.updated_at)

    latest_media = Multimedia.objects.order_by('-created_at').first()
    if latest_media and latest_media.created_at:
        candidates.append(latest_media.created_at)

    lastmod_dt = max(candidates) if candidates else timezone.now()
    context = {
        'lastmod': lastmod_dt.strftime('%Y-%m-%d'),
    }
    return render(request, 'sitemap.xml', context, content_type='application/xml')


@require_GET
def contact_form_view(request: HttpRequest) -> HttpResponse:
    """
    Retorna el fragmento del formulario limpio para HTMX.
    """
    form = services.get_contact_form()
    response = render(request, 'core/partials/contact_form.html', {'form': form})
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@require_POST
def contact(request: HttpRequest) -> HttpResponse:
    is_htmx = bool(getattr(request, 'htmx', None))
    wants_json = (
        not is_htmx
        and 'application/json' in request.headers.get('accept', '')
        and 'text/html' not in request.headers.get('accept', '')
    )

    ip = get_client_ip(request)
    rate_key = f"contact_rate_{ip}"
    attempts = cache.get(rate_key, 0)
    if attempts >= CONTACT_RATE_LIMIT:
        rate_error = "Has enviado demasiados mensajes en poco tiempo. Espera unos minutos antes de volver a intentarlo."
        if is_htmx:
            return render(request, 'core/partials/contact_form.html', {
                'form': services.get_contact_form(),
                'rate_limit_error': rate_error,
            }, status=429)
        if wants_json:
            return JsonResponse({'success': False, 'error': rate_error}, status=429)
        return render(
            request,
            'core/landing.html',
            {**_build_landing_context(), 'rate_limit_error': rate_error},
            status=429,
        )

    cache.set(rate_key, attempts + 1, CONTACT_RATE_WINDOW_SECONDS)

    result = services.process_contact_message(request.POST)

    if not result.get('success'):
        if is_htmx:
            return render(request, 'core/partials/contact_form.html', {
                'form': result.get('form'),
                'errors': result.get('errors'),
            }, status=422)
        if wants_json:
            return JsonResponse({'success': False, 'errors': result.get('errors')}, status=400)
        return render(
            request,
            'core/landing.html',
            _build_landing_context(form=result.get('form')),
            status=422,
        )

    if is_htmx:
        return render(request, 'core/partials/contact_success.html')
    if wants_json:
        return JsonResponse({'success': True, 'message': result.get('message')})
    return render(
        request,
        'core/landing.html',
        _build_landing_context(contact_submitted=True),
    )


def _build_legal_context():
    return {
        'fighter': services.get_active_fighter(),
        'social_networks': services.get_active_social_networks(),
    }


@require_GET
def legal_notice(request: HttpRequest) -> HttpResponse:
    """Página de Aviso Legal (LSSI-CE)."""
    return render(request, 'core/legal/aviso_legal.html', _build_legal_context())


@require_GET
def privacy_policy(request: HttpRequest) -> HttpResponse:
    """Página de Política de Privacidad (RGPD y LOPDGDD)."""
    return render(request, 'core/legal/politica_privacidad.html', _build_legal_context())


@require_GET
def cookie_policy(request: HttpRequest) -> HttpResponse:
    """Página de Política de Cookies (LSSI-CE Art. 22.2 y Guía AEPD)."""
    return render(request, 'core/legal/politica_cookies.html', _build_legal_context())


def gallery(request: HttpRequest) -> HttpResponse:
    media_type = request.GET.get('type', 'foto')

    if media_type not in ALLOWED_MEDIA_TYPES:
        media_type = 'foto'

    items = services.get_gallery_items(media_type=media_type, limit=12 if media_type == 'foto' else 6)

    context = {
        'items': items,
        'media_type': media_type,
    }

    response = render(request, 'core/partials/gallery_items.html', context)
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response