# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0019_alter_qualitycommission_coefficient_meetingminutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingminutes',
            name='minutes_file',
            field=models.FileField(blank=True, null=True, upload_to='meeting_minutes/', verbose_name='فایل صورت جلسه'),
        ),
        migrations.AlterField(
            model_name='meetingminutes',
            name='minutes_number',
            field=models.IntegerField(verbose_name='نتیجه صورت جلسه'),
        ),
    ]
