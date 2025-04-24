from django.db import migrations
from django.conf import settings

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Update the default site if it exists
    Site.objects.filter(id=settings.SITE_ID).delete()
    # Create the new site
    Site.objects.create(
        id=settings.SITE_ID,
        domain='localhost:8000',
        name='AgapeThrift'
    )

def reverse_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(id=settings.SITE_ID).delete()
    Site.objects.create(
        id=settings.SITE_ID,
        domain='example.com',
        name='example.com'
    )

class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(create_default_site, reverse_default_site),
    ] 