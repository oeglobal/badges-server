# Generated by Django 2.2.2 on 2019-08-05 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0002_auto_20190618_0854")]

    operations = [
        migrations.AddField(
            model_name="media",
            name="original_filename",
            field=models.TextField(default=""),
        )
    ]
