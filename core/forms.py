from django import forms
from .models import ContactMessage, Service


class ContactMessageForm(forms.ModelForm):
    # Campo trampa (Honeypot) invisible para humanos pero llenado por bots
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'off',
            'class': 'hidden',
            'aria-hidden': 'true',
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'service_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'contact-name',
                'class': 'form-input w-full px-4 py-3 rounded text-white focus:border-butcher-red focus:outline-none transition',
                'placeholder': 'Tu nombre',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'id': 'contact-email',
                'class': 'form-input w-full px-4 py-3 rounded text-white focus:border-butcher-red focus:outline-none transition',
                'placeholder': 'tu@email.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'id': 'contact-phone',
                'class': 'form-input w-full px-4 py-3 rounded text-white focus:border-butcher-red focus:outline-none transition',
                'placeholder': '+34 600 000 000',
            }),
            'service_type': forms.Select(attrs={
                'id': 'contact-service',
                'class': 'form-input w-full px-4 py-3 rounded text-white focus:border-butcher-red focus:outline-none transition',
            }),
            'message': forms.Textarea(attrs={
                'id': 'contact-message',
                'class': 'form-input w-full px-4 py-3 rounded text-white focus:border-butcher-red focus:outline-none transition',
                'placeholder': '¿Qué deseas aprender o consultar?',
                'rows': 4,
                'required': True,
            }),
        }
        labels = {
            'name': 'Nombre completo',
            'email': 'Email',
            'phone': 'Teléfono (opcional)',
            'service_type': 'Tipo de clase',
            'message': 'Mensaje',
        }
        error_messages = {
            'name': {
                'required': 'El nombre es requerido.',
                'max_length': 'El nombre no puede superar los 200 caracteres.',
            },
            'email': {
                'required': 'El email es requerido.',
                'invalid': 'Introduce una dirección de email válida.',
            },
            'phone': {
                'max_length': 'El teléfono no puede superar los 20 caracteres.',
            },
            'message': {
                'required': 'El mensaje es requerido.',
            },
        }

    def clean_website(self):
        value = self.cleaned_data.get('website', '')
        if value:
            raise forms.ValidationError("Spam detectado.")
        return value
