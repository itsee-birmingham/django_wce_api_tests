# Generated by Django 2.2 on 2021-10-30 11:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_tests', '0008_publicationplan_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(null=True)),
                ('created_by', models.TextField(blank=True, verbose_name='created_by')),
                ('last_modified_time', models.DateTimeField(null=True)),
                ('last_modified_by', models.TextField(blank=True, verbose_name='Last_modified_by')),
                ('version_number', models.IntegerField(null=True)),
                ('active', models.BooleanField(null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='project',
            name='editors',
            field=models.ManyToManyField(blank=True, related_name='editor_of', to='api_tests.Editor'),
        ),
        migrations.AlterField(
            model_name='project',
            name='managing_editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='manager', to='api_tests.Editor'),
        ),
    ]
