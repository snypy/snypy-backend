# Generated by Django 3.2.8 on 2021-10-11 21:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_userforeignkey.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snippets', '0003_relations'),
    ]

    operations = [
        migrations.CreateModel(
            name='SnippetFavorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snippet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snippet_favorites', to='snippets.snippet', verbose_name='Snippet')),
                ('user', django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='snippet_favorites', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
