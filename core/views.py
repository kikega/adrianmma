from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from . import services


def landing(request: HttpRequest) -> HttpResponse:
    """
    Vista principal de la landing page.
    Obtiene los datos necesarios desde la capa de servicios y renderiza la plantilla.
    """
    context = {
        'fighter': services.get_active_fighter(),
        'services': services.get_active_services(),
        'photos': list(services.get_gallery_items('foto', limit=6)),
        'videos': services.get_gallery_items('video', limit=6),
        'social_networks': services.get_active_social_networks(),
    }
    return render(request, 'core/landing.html', context)


def gallery(request: HttpRequest) -> HttpResponse:
    """
    Vista para cargar dinámicamente elementos de la galería mediante HTMX.
    """
    media_type = request.GET.get('type', 'foto')
    limit = 6 if media_type == 'foto' else 6
    items = services.get_gallery_items(media_type=media_type, limit=limit)
    
    context = {
        'items': items,
        'media_type': media_type,
    }
    if media_type == 'video':
        context['photos'] = services.get_gallery_items('foto', limit=6)
        
    return render(request, 'core/partials/gallery_items.html', context)


@require_POST
def contact(request: HttpRequest) -> HttpResponse:
    """
    Procesa el formulario de contacto.
    Maneja peticiones HTMX y peticiones estándar (JSON).
    """
    result = services.process_contact_message(request.POST)
    
    # Check if request comes from HTMX using django-htmx attribute
    is_htmx = hasattr(request, 'htmx') and request.htmx
    
    if not result.get('success'):
        if is_htmx:
            return render(request, 'core/partials/contact_form.html', {'errors': result.get('errors')})
        return JsonResponse(result, status=400)
    
    if is_htmx:
        return render(request, 'core/partials/contact_success.html')
    return JsonResponse(result)