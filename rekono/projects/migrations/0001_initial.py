# Generated by Django 3.2.12 on 2022-04-10 14:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import security.input_validation
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100, unique=True, validators=[security.input_validation.validate_name])),
                ('description', models.TextField(max_length=300, validators=[security.input_validation.validate_text])),
                ('defectdojo_product_id', models.IntegerField(blank=True, null=True, validators=[security.input_validation.validate_number])),
                ('defectdojo_engagement_id', models.IntegerField(blank=True, null=True, validators=[security.input_validation.validate_number])),
                ('defectdojo_engagement_by_target', models.BooleanField(default=False)),
                ('defectdojo_synchronization', models.BooleanField(default=False)),
                ('members', models.ManyToManyField(blank=True, related_name='members', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
    ]
