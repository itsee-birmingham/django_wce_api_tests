# Generated by Django 2.2 on 2021-10-29 13:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_tests', '0004_decision'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(null=True)),
                ('created_by', models.TextField(blank=True, verbose_name='created_by')),
                ('last_modified_time', models.DateTimeField(null=True)),
                ('last_modified_by', models.TextField(blank=True, verbose_name='Last_modified_by')),
                ('version_number', models.IntegerField(null=True)),
                ('status', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('genre', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('editors', models.ManyToManyField(blank=True, related_name='editor_of', to=settings.AUTH_USER_MODEL)),
                ('managing_editor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='manager', to=settings.AUTH_USER_MODEL)),
                ('work', models.ManyToManyField(blank=True, related_name='included_in', to='api_tests.Work')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
