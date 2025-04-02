

from django.db import migrations, models


class Migration(migrations.Migration):

    #  This migration comes after the one that removed fields
    dependencies = [
        ('delta', '0005_remove_request_date_updated_and_more'),
    ]

    operations = [
        #  Add explanation field back to Request model
        migrations.AddField(
            model_name='request',
            name='explanation',
            field=models.TextField(blank=True, null=True),
        ),
        #  Add first_name field back
        migrations.AddField(
            model_name='request',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        #  Add last_name field back
        migrations.AddField(
            model_name='request',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
