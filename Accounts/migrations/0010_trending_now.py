# Generated by Django 5.0.7 on 2024-12-26 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0009_alter_latestevent_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trending_now',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Upload a trending now image.', upload_to='Trending_now/')),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Order of appearance in the section.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Trending_now',
                'verbose_name_plural': 'Trending_now',
                'ordering': ['display_order'],
            },
        ),
    ]