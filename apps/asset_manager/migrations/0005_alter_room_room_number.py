# Generated by Django 5.0 on 2024-05-12 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_manager', '0004_remove_tenant_suite_tenant_suite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_number',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
