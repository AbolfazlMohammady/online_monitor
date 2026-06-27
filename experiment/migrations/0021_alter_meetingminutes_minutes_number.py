# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0020_meetingminutes_minutes_file_and_result_label'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='meetingminutes',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='meetingminutes',
            name='minutes_number',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='نتیجه صورت جلسه'),
        ),
    ]
