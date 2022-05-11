# Generated by Django 4.0.4 on 2022-05-10 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0007_blacksmithformula_monster_item_desc_item_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='atk',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='deff',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='imageAlt',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='imgSrc',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='notes',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='desc',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='item',
            name='type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Item Type'),
        ),
    ]
