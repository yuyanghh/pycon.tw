# Generated by Django 3.0.3 on 2020-09-02 07:49

import core.models
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0047_auto_20200630_2342'),
        ('events', '0028_auto_20200902_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposedtalkevent',
            name='proposal',
            field=core.models.BigForeignKey(limit_choices_to={'accepted': True}, on_delete=django.db.models.deletion.CASCADE, to='proposals.TalkProposal', unique=True, verbose_name='proposal'),
        ),
        migrations.AlterField(
            model_name='proposedtutorialevent',
            name='proposal',
            field=core.models.BigForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proposals.TutorialProposal', unique=True, verbose_name='proposal'),
        ),
    ]
