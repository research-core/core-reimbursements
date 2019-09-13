# Generated by Django 2.2.1 on 2019-09-12 12:43

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursements', '0024_auto_20190911_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerDiem',
            fields=[
                ('expense_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reimbursements.Expense')),
                ('purpose', models.CharField(max_length=255, verbose_name='Travel purpose')),
                ('local', models.CharField(blank=True, max_length=255, null=True, verbose_name='Local')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('n_nights', models.PositiveSmallIntegerField(default=0, verbose_name='Number of nights for reimbursement')),
                ('start_working', models.DateField(verbose_name='Day you start working')),
                ('end_working', models.DateField(verbose_name='Day you end working')),
                ('prove_working', models.FileField(blank=True, null=True, upload_to='', verbose_name='Certificate of attendance')),
                ('start_travel', models.DateField(verbose_name='Day your travel started')),
                ('end_travel', models.DateField(verbose_name='Day your travel ended')),
                ('boarding_pass', models.FileField(blank=True, null=True, upload_to='', verbose_name='Boarding pass')),
            ],
            bases=('reimbursements.expense',),
        ),
    ]
