from django.db import migrations


def create_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")

    Site.objects.update_or_create(
        id=1,
        defaults={
            "domain": "pingger.pingger.blitz.cloud",
            "name": "Pingger",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0007_alert"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(
            create_site,
            migrations.RunPython.noop,
        ),
    ]