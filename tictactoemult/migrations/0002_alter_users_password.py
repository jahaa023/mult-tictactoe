# Generated by Django 5.1.4 on 2025-01-03 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tictactoemult', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='password',
            field=models.CharField(max_length=255),
        ),
    ]