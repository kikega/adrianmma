from django import forms
from .models import ContactMessage, Service


class ContactMessageForm(forms.ModelForm):
    # Campo trampa (Honeypot) invisible para humanos pero completado por bots
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'new-password',
            'aria-hidden': 'true',
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'service_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'contact-name',
                'class': 'form-input w-full px-4 py-3 rounded text-white transition',
                'placeholder': 'Tu nombre',
                'autocomplete': 'name',
                'maxlength': '200',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'id': 'contact-email',
                'class': 'form-input w-full px-4 py-3 rounded text-white transition',
                'placeholder': 'tu@email.com',
                'autocomplete': 'email',
                'inputmode': 'email',
                'autocapitalize': 'off',
                'autocorrect': 'off',
                'spellcheck': 'false',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'id': 'contact-phone',
                'type': 'tel',
                'class': 'form-input w-full px-4 py-3 rounded text-white transition',
                'placeholder': '+34 600 000 000',
                'autocomplete': 'tel',
                'inputmode': 'tel',
                'maxlength': '20',
            }),
            'service_type': forms.Select(attrs={
                'id': 'contact-service',
                'class': 'form-input w-full px-4 py-3 rounded text-white transition',
            }),
            'message': forms.Textarea(attrs={
                'id': 'contact-message',
                'class': 'form-input w-full px-4 py-3 rounded text-white transition',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service_type'].choices = [
            ('', 'Selecciona una disciplina (opcional)'),
            *Service.SERVICE_TYPES,
        ]
        if self.is_bound:
            self._apply_error_aria_attributes()

    def _apply_error_aria_attributes(self):
        """Añade aria-invalid y aria-describedby a los campos con errores tras validar."""
        for field_name, field in self.fields.items():
            if field_name == 'website':
                continue
            field_id = field.widget.attrs.get('id', f'id_{field_name}')
            if field_name in self.errors:
                field.widget.attrs['aria-invalid'] = 'true'
                field.widget.attrs['aria-describedby'] = f'{field_id}-error'

    def full_clean(self):
        super().full_clean()
        self._apply_error_aria_attributes()

    def clean_name(self):
        value = self.cleaned_data.get('name', '')
        cleaned = ' '.join(value.replace('\r', ' ').replace('\n', ' ').split())
        if not cleaned:
            raise forms.ValidationError('El nombre es requerido.')
        return cleaned

    def clean_website(self):
        value = self.cleaned_data.get('website', '')
        if value:
            raise forms.ValidationError("No se pudo procesar el envío. Inténtalo de nuevo.")
        return value
