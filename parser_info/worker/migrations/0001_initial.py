# Generated by Django 4.0.1 on 2022-01-21 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('news_id', models.IntegerField(primary_key=True, serialize=False)),
                ('header', models.CharField(max_length=256)),
                ('link', models.URLField()),
                ('img', models.ImageField(upload_to='')),
                ('text', models.TextField()),
            ],
        ),
    ]
