# Generated by Django 4.1 on 2022-09-07 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_likepost"),
    ]

    operations = [
        migrations.AddField(
            model_name="post", name="no_of_likes", field=models.IntegerField(default=0),
        ),
    ]
