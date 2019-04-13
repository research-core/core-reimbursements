# Generated by Django 2.2 on 2019-04-13 22:13

from django.db import migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursements', '0011_auto_20190411_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reimbursement',
            name='status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default='0', max_length=100, no_check_for_status=True, verbose_name='status'),
        ),
    ]