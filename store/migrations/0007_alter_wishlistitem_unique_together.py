# Generated by Django 5.1.2 on 2024-11-06 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_wishlistitem_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wishlistitem',
            unique_together=set(),
        ),
    ]
