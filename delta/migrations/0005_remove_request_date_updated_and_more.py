

from django.db import migrations, models


class Migration(migrations.Migration):

    #  Depends on the merged migration file before this
    dependencies = [
        ('delta', '0004_merge_20250317_1152'),
    ]

    operations = [
        #  Remove unused fields from the Request model
        migrations.RemoveField(
            model_name='request',
            name='date_updated',
        ),
        migrations.RemoveField(
            model_name='request',
            name='explanation',
        ),
        migrations.RemoveField(
            model_name='request',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='request',
            name='last_name',
        ),

        #  Make date_created auto-set on creation
        migrations.AlterField(
            model_name='request',
            name='date_created',
            field=models.DateField(auto_now_add=True),
        ),

        #  Update where PDFs are saved
        migrations.AlterField(
            model_name='request',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='generated_pdfs/'),
        ),

        # ✏️ Ensure request_type is just a plain string field now
        migrations.AlterField(
            model_name='request',
            name='request_type',
            field=models.CharField(max_length=20),
        ),
    ]
