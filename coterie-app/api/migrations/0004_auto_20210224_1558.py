# Generated by Django 3.1.7 on 2021-02-24 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
    ]