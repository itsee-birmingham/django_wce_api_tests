# Generated by Django 2.2 on 2021-10-30 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_tests', '0012_publicationplan_editors'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationplan',
            name='public',
            field=models.BooleanField(null=True),
        ),
    ]