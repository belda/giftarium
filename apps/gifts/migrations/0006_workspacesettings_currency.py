import apps.gifts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gifts', '0005_workspace_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacesettings',
            name='currency',
            field=models.CharField(
                default=apps.gifts.models._default_currency,
                help_text='Currency symbol shown next to prices (e.g. CZK, EUR, USD).',
                max_length=10,
                verbose_name='Currency',
            ),
        ),
    ]
