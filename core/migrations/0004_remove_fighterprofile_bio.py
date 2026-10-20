from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_multimedia_video_file"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fighterprofile",
            name="bio",
        ),
    ]
