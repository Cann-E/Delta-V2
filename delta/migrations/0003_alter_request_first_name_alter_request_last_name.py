

from django.db import migrations, models


class Migration(migrations.Migration):

    #  Depends on the previous migration
    dependencies = [
        ('delta', '0002_request_explanation_request_first_name_and_more'),
    ]

    operations = [
        #  Change 'first_name' to require a value (default: 'Unknown')
        migrations.AlterField(
            model_name='request',
            name='first_name',
            field=models.CharField(default='Unknown', max_length=50),
            preserve_default=False,  # 🧷 Don’t keep the old default
        ),
        #  Change 'last_name' to require a value (default: 'Unknown')
        migrations.AlterField(
            model_name='request',
            name='last_name',
            field=models.CharField(default='Unknown', max_length=50),
            preserve_default=False,
        ),
    ]
