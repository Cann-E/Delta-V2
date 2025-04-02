

from django.db import migrations, models


class Migration(migrations.Migration):

    #  Depends on the last migration where fields were added back
    dependencies = [
        ('delta', '0006_request_explanation_request_first_name_and_more'),
    ]

    operations = [
        #  Add UH ID field to CustomUser model
        migrations.AddField(
            model_name='customuser',
            name='uh_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
