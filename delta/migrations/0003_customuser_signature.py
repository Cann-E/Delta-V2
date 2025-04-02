

from django.db import migrations, models


class Migration(migrations.Migration):

    #  This migration depends on the previous one in the 'delta' app
    dependencies = [
        ('delta', '0002_remove_customuser_signature_alter_customuser_groups_and_more'),
    ]

    operations = [
        #  Add 'signature' field to the CustomUser model (for profile signatures)
        migrations.AddField(
            model_name='customuser',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to='signatures/'),  # 📁 Uploads go to 'signatures/' folder
        ),
    ]
