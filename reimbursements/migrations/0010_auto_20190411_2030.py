# Generated by Django 2.2 on 2019-04-11 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursements', '0009_auto_20190411_2020'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reimbursement',
            options={'ordering': ('-created',), 'permissions': (('can_approve_reimbursements', 'Approve or reject reimbursements'),), 'verbose_name': 'Reimbursement', 'verbose_name_plural': 'Reimbursements'},
        ),
    ]