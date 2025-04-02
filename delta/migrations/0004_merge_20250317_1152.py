

from django.db import migrations


class Migration(migrations.Migration):

    #  This migration depends on two previous ones (merged branch migrations)
    dependencies = [
        ('delta', '0003_alter_request_first_name_alter_request_last_name'),  #  From one branch
        ('delta', '0003_customuser_signature'),  #  From another branch
    ]

    #  No operations here — it's just to merge branches/migrations together
    operations = [
    ]
