# Generated by Django 4.2.2 on 2024-06-19 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_remove_user_user_c_alter_charge_sheet_main_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='remark',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='charge_sheet',
            name='investigation',
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='charge_sheet',
            name='main_user',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
