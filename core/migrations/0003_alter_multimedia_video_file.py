import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_populate_seed_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="multimedia",
            name="video_file",
            field=models.FileField(
                blank=True,
                upload_to="multimedia/videos/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["mp4", "webm", "mov", "avi", "mkv"]
                    )
                ],
            ),
        ),
    ]
