# Generated by Django 5.1.7 on 2025-04-19 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_remove_newcomment_travelid_newcomment_traveltittle"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="newcomment",
            name="creatTime",
        ),
    ]
