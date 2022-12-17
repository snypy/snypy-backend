# Generated by Django 4.1.2 on 2022-12-17 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentPage',
            fields=[
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(primary_key=True, serialize=False, unique=True)),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'Content Page',
                'verbose_name_plural': 'Content Pages',
            },
        ),
    ]
