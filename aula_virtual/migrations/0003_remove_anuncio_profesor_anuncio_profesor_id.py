# Generated by Django 4.1.1 on 2024-07-02 02:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aula_virtual', '0002_alter_asistencia_jornada_anuncio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anuncio',
            name='profesor',
        ),
        migrations.AddField(
            model_name='anuncio',
            name='profesor_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
