from django.contrib import admin
from django.utils.html import format_html
from .models import FighterProfile, Service, Multimedia, SocialNetwork, ContactMessage


@admin.register(FighterProfile)
class FighterProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'nickname', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name', 'nickname']
    fieldsets = (
        ('Información Personal', {
            'fields': ('name', 'nickname', 'bio', 'profile_image')
        }),
        ('specialties', {
            'fields': ('specialties', 'achievements')
        }),
        ('Contacto', {
            'fields': ('email', 'phone', 'location')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_hour', 'is_active', 'order']
    list_filter = ['is_active']
    ordering = ['order']


class MultimediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type', 'is_featured', 'created_at']
    list_filter = ['media_type', 'is_featured']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Información', {
            'fields': ('title', 'media_type', 'description')
        }),
        ('Contenido', {
            'fields': ('image', 'video_url', 'video_file')
        }),
        ('Opciones', {
            'fields': ('is_featured',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, **kwargs)


admin.site.register(Multimedia, MultimediaAdmin)


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'username', 'url', 'is_active', 'order']
    list_filter = ['platform', 'is_active']
    list_editable = ['is_active', 'order']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service_type', 'is_read', 'created_at']
    list_filter = ['is_read', 'service_type', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marcar como leídos"