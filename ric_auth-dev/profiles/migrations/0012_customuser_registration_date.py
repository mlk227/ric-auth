# Generated by Django 3.1.3 on 2021-02-16 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_add_sub_group_related_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='registration_date',
            field=models.DateField(help_text='Service registration date of the user', null=True),
        ),
    ]
