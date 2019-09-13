# Generated by Django 2.2.1 on 2019-09-12 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursements', '0026_reimbursement_fullname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reimbursement',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='humanresources.Person'),
        ),
    ]