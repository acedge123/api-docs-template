# Generated manually to replace ArrayField with TextField for SQLite compatibility

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoringengine', '0031_create_cache_table'),
    ]

    operations = [
        # Remove the old ArrayField and replace with TextField
        migrations.AlterField(
            model_name='answer',
            name='values',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='answerlog',
            name='values',
            field=models.TextField(blank=True, null=True),
        ),
    ]
