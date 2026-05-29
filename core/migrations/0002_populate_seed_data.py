from django.db import migrations

def populate_seed_data(apps, schema_editor):
    FighterProfile = apps.get_model('core', 'FighterProfile')
    Service = apps.get_model('core', 'Service')
    Multimedia = apps.get_model('core', 'Multimedia')
    
    # 1. Crear el Perfil del Luchador si no existe
    fighter, created = FighterProfile.objects.get_or_create(
        email="contacto@adrigalvez.com",
        defaults={
            "name": "Adrián Gálvez",
            "nickname": "The Butcher",
            "bio": "Adrián Gálvez 'The Butcher' es un luchador y entrenador profesional de MMA (Artes Marciales Mixtas), cinturón negro de Jiu-Jitsu Brasileño, competidor en circuitos profesionales y campeón nacional. Ofrece entrenamiento personalizado de alto rendimiento.",
            "specialties": "MMA, Jiu-Jitsu, Boxeo, Defensa Personal",
            "achievements": "Campeón de España Amateur IMAF 2021\nCompetidor WAR\nCircuito Profesional de MMA",
            "phone": "+34 666 666 666",
            "location": "Alicante - Climent Club",
            "profile_image": "fighter/Imagen pegada.png",
            "is_active": True
        }
    )
    
    # 2. Crear los Servicios
    services_data = [
        {
            "name": "defensa_personal",
            "description": "Técnicas de protección y control",
            "price_per_hour": 35.00,
            "order": 1
        },
        {
            "name": "jiujitsu",
            "description": "Arte brasilero - Gi & No-Gi",
            "price_per_hour": 40.00,
            "order": 2
        },
        {
            "name": "boxeo",
            "description": "Técnicas de puño",
            "price_per_hour": 30.00,
            "order": 3
        },
        {
            "name": "mma",
            "description": "Artes marciales mixtas",
            "price_per_hour": 50.00,
            "order": 4
        }
    ]
    for s_data in services_data:
        Service.objects.get_or_create(name=s_data["name"], defaults=s_data)
        
    # 3. Crear elementos multimedia (Fotos)
    photos_data = [
        {"title": "Combate Sangriento", "image": "multimedia/photos/adri-sangriento.jpg"},
        {"title": "Victoria y Cinturón", "image": "multimedia/photos/adri-campeon.png"},
        {"title": "Entrenamiento en Guardia", "image": "multimedia/photos/adri-guardia.jpeg"},
        {"title": "Equipo Climent Club", "image": "multimedia/photos/equipo-climent.png"},
        {"title": "Preparación del Combate", "image": "multimedia/photos/WhatsApp Image 2023-12-06 at 14.56.05.jpeg"},
        {"title": "Acción en el Ring", "image": "multimedia/photos/Captura desde 2026-03-29 18-19-50.png"},
        {"title": "Entrenamiento Diario", "image": "multimedia/photos/Captura desde 2026-03-29 18-13-23.png"},
        {"title": "Preparación Física", "image": "multimedia/photos/Captura desde 2026-04-23 17-31-34.png"},
        {"title": "Entrenamiento con Compañeros", "image": "multimedia/photos/adri-jorge-agus.png"},
    ]
    for p_data in photos_data:
        Multimedia.objects.get_or_create(
            title=p_data["title"],
            media_type="foto",
            defaults={"image": p_data["image"], "is_featured": True}
        )
        
    # 4. Crear elementos multimedia (Vídeos de YouTube)
    videos_data = [
        {
            "title": "Highlight de Combate - Adrián Gálvez",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "image": "multimedia/photos/adri-sangriento.jpg"
        },
        {
            "title": "Sesión de Sparring en Climent Club",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "image": "multimedia/photos/adri-guardia.jpeg"
        },
        {
            "title": "Técnicas de Sumisión de Jiu-Jitsu",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "image": "multimedia/photos/adri-jorge-agus.png"
        }
    ]
    for v_data in videos_data:
        Multimedia.objects.get_or_create(
            title=v_data["title"],
            media_type="video",
            defaults={
                "video_url": v_data["video_url"],
                "image": v_data["image"],
                "is_featured": True
            }
        )

def rollback_seed_data(apps, schema_editor):
    FighterProfile = apps.get_model('core', 'FighterProfile')
    Service = apps.get_model('core', 'Service')
    Multimedia = apps.get_model('core', 'Multimedia')
    
    FighterProfile.objects.filter(email="contacto@adrigalvez.com").delete()
    Service.objects.all().delete()
    Multimedia.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_seed_data, rollback_seed_data),
    ]
