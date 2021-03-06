# Generated by Django 2.2 on 2021-10-28 17:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(null=True)),
                ('created_by', models.TextField(blank=True, verbose_name='created_by')),
                ('last_modified_time', models.DateTimeField(null=True)),
                ('last_modified_by', models.TextField(blank=True, verbose_name='Last_modified_by')),
                ('version_number', models.IntegerField(null=True)),
                ('identifier', models.TextField(unique=True, verbose_name='Identifier')),
                ('name', models.TextField(blank=True, verbose_name='Name')),
                ('age', models.IntegerField(blank=True, null=True, verbose_name='Age')),
                ('date_joined', models.DateField(null=True, verbose_name='Date Joined')),
                ('active', models.BooleanField(null=True, verbose_name='Active')),
            ],
            options={
                'ordering': ['identifier'],
            },
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(null=True)),
                ('created_by', models.TextField(blank=True, verbose_name='created_by')),
                ('last_modified_time', models.DateTimeField(null=True)),
                ('last_modified_by', models.TextField(blank=True, verbose_name='Last_modified_by')),
                ('version_number', models.IntegerField(null=True)),
                ('identifier', models.TextField(blank=True, verbose_name='Identifier')),
                ('title', models.TextField(blank=True, verbose_name='Title')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='works', to='api_tests.Author')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(null=True)),
                ('created_by', models.TextField(blank=True, verbose_name='created_by')),
                ('last_modified_time', models.DateTimeField(null=True)),
                ('last_modified_by', models.TextField(blank=True, verbose_name='Last_modified_by')),
                ('version_number', models.IntegerField(null=True)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('score', models.IntegerField(blank=True, null=True, verbose_name='Score')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reviewers', to=settings.AUTH_USER_MODEL)),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reviews', to='api_tests.Work')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
