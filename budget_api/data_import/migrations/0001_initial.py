# Generated by Django 4.2.3 on 2023-10-11 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImportFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=128)),
                ('headers', models.JSONField(null=True)),
                ('content', models.JSONField(null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
