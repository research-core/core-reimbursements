# Generated by Django 2.1.7 on 2019-03-19 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursements', '0002_auto_20190319_1412'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reimbursement',
            options={'ordering': ('-created',), 'permissions': (('can_request_for_other', 'Request on behalf of someone else '), ('can_print', 'Print Reimbursement'), ('can_approve', 'Approve or reject Reimbursements'))},
        ),
    ]
