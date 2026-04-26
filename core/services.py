from typing import Dict, Any, List, Optional
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from .models import FighterProfile, Service, Multimedia, SocialNetwork, ContactMessage

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

def get_gallery_items(media_type: str, limit: Optional[int] = None) -> QuerySet[Multimedia]:
    """
    Obtiene los elementos multimedia según su tipo.
    
    Args:
        media_type (str): Tipo de multimedia ('foto' o 'video').
        limit (int, optional): Límite de resultados a retornar.
        
    Returns:
        QuerySet[Multimedia]: Lista de elementos multimedia filtrados.
    """
    items = Multimedia.objects.filter(media_type=media_type)
    if limit:
        return items[:limit]
    return items

def get_active_social_networks() -> QuerySet[SocialNetwork]:
    """
    Obtiene las redes sociales activas ordenadas por su campo order.
    """
    return SocialNetwork.objects.filter(is_active=True).order_by('order')

def process_contact_message(data: Dict[str, str]) -> Dict[str, Any]:
    """
    Procesa, valida y guarda un mensaje de contacto.
    
    Args:
        data (Dict[str, str]): Datos del formulario de contacto.
        
    Returns:
        Dict[str, Any]: Diccionario con el resultado de la operación.
            Contiene 'success' (bool) y 'errors' (Dict) si falla, o 'message' si acierta.
    """
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    service_type = data.get('service_type', '')
    message_text = data.get('message', '').strip()
    
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
    if not message_text:
        errors['message'] = 'El mensaje es requerido'
    
    if errors:
        return {'success': False, 'errors': errors}
        
    ContactMessage.objects.create(
        name=name,
        email=email,
        phone=phone,
        service_type=service_type,
        message=message_text
    )
    
    return {'success': True, 'message': 'Mensaje enviado correctamente'}
