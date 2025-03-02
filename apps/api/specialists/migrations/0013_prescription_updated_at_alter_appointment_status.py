# Generated by Django 5.0 on 2024-07-20 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('specialists', '0012_remove_prescription_diagnosis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('rejected', 'Rejected'), ('In Progress', 'In Progress')], default='Pending', max_length=20),
        ),
    ]
