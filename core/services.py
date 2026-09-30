import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import QuerySet

from .models import FighterProfile, Service, Multimedia, SocialNetwork, ContactMessage
from .forms import ContactMessageForm

logger = logging.getLogger('core')

ALLOWED_MEDIA_TYPES = {'foto', 'video'}

def get_active_fighter() -> Optional[FighterProfile]:
    """
    Obtiene el perfil del luchador activo.
    """
    return FighterProfile.objects.filter(is_active=True).first()

def get_active_services() -> QuerySet[Service]:
    """
    Obtiene todos los servicios activos ordenados por el campo order.
    """
    return Service.objects.filter(is_active=True).order_by('order')

def get_gallery_items(media_type: str, limit: Optional[int] = None, featured_only: bool = False) -> QuerySet[Multimedia]:
    """
    Obtiene elementos de la galería filtrados por tipo.
    """
    if media_type not in ALLOWED_MEDIA_TYPES:
        return Multimedia.objects.none()

    items = Multimedia.objects.filter(media_type=media_type)
    if featured_only:
        items = items.filter(is_featured=True)
    if limit:
        return items[:limit]
    return items

def get_active_social_networks() -> QuerySet[SocialNetwork]:
    """
    Obtiene las redes sociales activas ordenadas por su campo order.
    """
    return SocialNetwork.objects.filter(is_active=True).order_by('order')

def get_contact_form() -> ContactMessageForm:
    """
    Retorna una instancia vacía del formulario de contacto.
    """
    return ContactMessageForm()

def process_contact_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida y procesa el mensaje de contacto mediante ContactMessageForm,
    con protección honeypot anti-spam y notificación por email.
    """
    form = ContactMessageForm(data)
    if not form.is_valid():
        return {
            'success': False,
            'form': form,
            'errors': form.errors,
        }

    contact_message = form.save()

    # Enviar notificación por email al entrenador/administrador
    try:
        subject = f"[Web Contacto] Nuevo mensaje de {contact_message.name}"
        service_label = contact_message.get_service_type_display() if contact_message.service_type else 'No especificado'
        body = (
            f"Has recibido un nuevo mensaje desde la web:\n\n"
            f"Nombre: {contact_message.name}\n"
            f"Email: {contact_message.email}\n"
            f"Teléfono: {contact_message.phone or 'No aportado'}\n"
            f"Servicio de interés: {service_label}\n"
            f"Fecha: {contact_message.created_at.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Mensaje:\n{contact_message.message}\n"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'web@adrigalvez.com'),
            recipient_list=[getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', 'contacto@adrigalvez.com')],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Error al enviar email de notificación de contacto: {e}")

    return {
        'success': True,
        'message': 'Mensaje enviado correctamente',
        'instance': contact_message,
        'form': form,
    }
