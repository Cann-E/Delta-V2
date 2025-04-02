

from django.db import migrations, models


class Migration(migrations.Migration):

    #  This migration depends on Django auth app + your app's first migration
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('delta', '0001_initial'),
    ]

    operations = [
        #  Remove 'signature' field from CustomUser model
        migrations.RemoveField(
            model_name='customuser',
            name='signature',
        ),
        #  Update 'groups' field to use custom related_name + help text
        migrations.AlterField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                help_text='The groups this user belongs to.',
                related_name='customuser_set',
                related_query_name='customuser',
                to='auth.group',
                verbose_name='groups'
            ),
        ),
        # Same for 'user_permissions' field
        migrations.AlterField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(
                blank=True,
                help_text='Specific permissions for this user.',
                related_name='customuser_set',
                related_query_name='customuser',
                to='auth.permission',
                verbose_name='user permissions'
            ),
        ),
    ]
