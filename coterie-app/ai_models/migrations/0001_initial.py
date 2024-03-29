# Generated by Django 3.1.7 on 2021-08-24 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AiModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=600)),
                ('model_id', models.PositiveIntegerField()),
                ('version_id', models.PositiveIntegerField()),
                ('gcr_url', models.CharField(max_length=1000)),
                ('description', models.CharField(default='', max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('id',),
                'unique_together': {('model_id', 'version_id')},
            },
        ),
    ]
