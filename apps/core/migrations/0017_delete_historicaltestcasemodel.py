from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_testcasescript_script_location'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HistoricalTestCaseModel',
        ),
    ]
