# Generated by Django 5.1.4 on 2024-12-24 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0003_alter_student_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='user',
            new_name='username',
        ),
    ]