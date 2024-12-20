# Generated by Django 5.0.7 on 2024-12-15 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0003_blog'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title displayed on the slide', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Short description or content for the slide')),
                ('image', models.ImageField(help_text='Image displayed as the slide background', upload_to='slider_images/')),
                ('link', models.URLField(blank=True, help_text='URL to navigate to when the slide is clicked', null=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Order in which the slide appears')),
                ('is_active', models.BooleanField(default=True, help_text='Mark as true to display this slide')),
            ],
            options={
                'verbose_name': 'Slider',
                'verbose_name_plural': 'Sliders',
                'ordering': ['order'],
            },
        ),
    ]
