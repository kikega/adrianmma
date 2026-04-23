from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import FighterProfile, Service, Multimedia, SocialNetwork, ContactMessage


def landing(request):
    fighter = FighterProfile.objects.filter(is_active=True).first()
    services = Service.objects.filter(is_active=True).order_by('order')
    photos = Multimedia.objects.filter(media_type='foto')[:12]
    videos = Multimedia.objects.filter(media_type='video')[:6]
    social_networks = SocialNetwork.objects.filter(is_active=True).order_by('order')
    
    context = {
        'fighter': fighter,
        'services': services,
        'photos': list(photos),
        'videos': videos,
        'social_networks': social_networks,
    }
    return render(request, 'core/landing.html', context)


def gallery(request):
    media_type = request.GET.get('type', 'foto')
    items = Multimedia.objects.filter(media_type=media_type)
    
    return render(request, 'core/partials/gallery_items.html', {'items': items})


@csrf_exempt
@require_POST
def contact(request):
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    service_type = request.POST.get('service_type', '')
    message = request.POST.get('message', '').strip()
    
    errors = {}
    if not name:
        errors['name'] = 'El nombre es requerido'
    if not email:
        errors['email'] = 'El email es requerido'
    elif email:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Email inválido'
    if not message:
        errors['message'] = 'El mensaje es requerido'
    
    if errors:
        if request.htmx:
            return render(request, 'core/partials/contact_form.html', {'errors': errors})
        return JsonResponse({'success': False, 'errors': errors})
    
    ContactMessage.objects.create(
        name=name,
        email=email,
        phone=phone,
        service_type=service_type,
        message=message
    )
    
    if request.htmx:
        return render(request, 'core/partials/contact_success.html')
    return JsonResponse({'success': True, 'message': 'Mensaje enviado correctamente'})