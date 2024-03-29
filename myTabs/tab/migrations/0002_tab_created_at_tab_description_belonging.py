# Generated by Django 4.2.1 on 2023-06-03 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tab', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tab',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tab',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='Belonging',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('tab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tab.tab')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
