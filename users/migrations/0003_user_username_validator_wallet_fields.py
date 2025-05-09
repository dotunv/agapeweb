# Generated by Django 5.2 on 2023-06-01 12:00

from django.db import migrations, models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_google_id_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pre_starter_wallet',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='user',
            name='starter_wallet',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(
                help_text=_('Required. 150 characters or fewer. Single word with letters and numbers only.'),
                max_length=150,
                unique=True,
                validators=[
                    RegexValidator(
                        regex=r'^[a-zA-Z0-9]+$',
                        message='Username must be a single word containing only letters and numbers.'
                    )
                ],
                verbose_name='username'
            ),
        ),
    ]