from django.db import migrations, models
import django.utils.timezone

def map_fields(apps, schema_editor):
    PressRelease = apps.get_model('core', 'PressRelease')
    for pr in PressRelease.objects.all():
        pr.header = pr.intro
        pr.footer = pr.signed_by
        pr.save()

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_editableelement_tabsettings"),
    ]

    operations = [
        # Add new fields
        migrations.AddField(
            model_name='pressrelease',
            name='header',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='pressrelease',
            name='footer',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='pressrelease',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='decrees/'),
        ),
        migrations.AddField(
            model_name='pressrelease',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pressrelease',
            name='published_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        # Migrate data
        migrations.RunPython(map_fields),
        # Remove old fields
        migrations.RemoveField(
            model_name='pressrelease',
            name='intro',
        ),
        migrations.RemoveField(
            model_name='pressrelease',
            name='signed_by',
        ),
    ]
