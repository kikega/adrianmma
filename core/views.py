from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache

from . import services


ALLOWED_MEDIA_TYPES = {'foto', 'video'}


def landing(request: HttpRequest) -> HttpResponse:
    fighter = services.get_active_fighter()
    services_qs = services.get_active_services()
    photos = services.get_gallery_items('foto', limit=6)
    videos = services.get_gallery_items('video', limit=6)
    social = services.get_active_social_networks()

    context = {
        'fighter': fighter,
        'services': services_qs,
        'photos': list(photos),
        'videos': videos,
        'social_networks': social,
    }
    return render(request, 'core/landing.html', context)


def gallery(request: HttpRequest) -> HttpResponse:
    media_type = request.GET.get('type', 'foto')

    if media_type not in ALLOWED_MEDIA_TYPES:
        media_type = 'foto'

    items = services.get_gallery_items(media_type=media_type, limit=6)

    context = {
        'items': items,
        'media_type': media_type,
    }

    if media_type == 'video':
        gallery_photos = cache.get('gallery_photos_preview')
        if gallery_photos is None:
            gallery_photos = list(services.get_gallery_items('foto', limit=6))
            cache.set('gallery_photos_preview', gallery_photos, 300)
        context['photos'] = gallery_photos

    return render(request, 'core/partials/gallery_items.html', context)


@require_POST
def contact(request: HttpRequest) -> HttpResponse:
    result = services.process_contact_message(request.POST)

    is_htmx = bool(getattr(request, 'htmx', None))

    if not result.get('success'):
        if is_htmx:
            return render(request, 'core/partials/contact_form.html', {'errors': result.get('errors')})
        return JsonResponse(result, status=400)

    if is_htmx:
        return render(request, 'core/partials/contact_success.html')
    return JsonResponse(result)