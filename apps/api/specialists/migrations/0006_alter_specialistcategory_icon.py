# Generated by Django 5.0 on 2024-07-08 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('specialists', '0005_alter_diagnosis_id_alter_prescription_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialistcategory',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='specialistCategory_images/'),
        ),
    ]
