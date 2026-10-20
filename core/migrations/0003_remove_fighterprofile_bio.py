from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_populate_seed_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fighterprofile",
            name="bio",
        ),
    ]
