# Generated by Django 3.2.10 on 2022-01-04 06:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tools', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=30, unique=True)),
                ('description', models.TextField(max_length=250)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=1)),
                ('configuration', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tools.configuration')),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='processes.process')),
                ('tool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.tool')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
