

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    #  Depends on the first migration of the 'delta' app
    dependencies = [
        ('delta', '0001_initial'),
    ]

    operations = [
        #  Add 'explanation' field to the Request model (optional text)
        migrations.AddField(
            model_name='request',
            name='explanation',
            field=models.TextField(blank=True, null=True),
        ),
        #  Add 'first_name' field (optional string)
        migrations.AddField(
            model_name='request',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        #  Add 'last_name' field (optional string)
        migrations.AddField(
            model_name='request',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        #  Change default value of 'date_created' to use today's date
        migrations.AlterField(
            model_name='request',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
