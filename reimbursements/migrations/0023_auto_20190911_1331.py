# Generated by Django 2.2.1 on 2019-09-11 12:31

from django.db import migrations
import djmoney.models.fields
import djmoney.models.validators
import djmoney.money


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursements', '0022_auto_20190607_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='value',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='EUR', max_digits=11, validators=[djmoney.models.validators.MinMoneyValidator(djmoney.money.Money(0.01))], verbose_name='Amount'),
        ),
    ]