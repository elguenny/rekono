# Generated by Django 3.2.12 on 2022-02-05 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tasks', '0001_initial'),
        ('tools', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='configuration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tools.configuration'),
        ),
    ]
