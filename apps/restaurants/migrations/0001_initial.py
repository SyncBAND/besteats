# Generated by Django 5.1 on 2024-09-05 18:17

import django.db.models.deletion
import django.db.models.functions.text
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('name', models.CharField(max_length=128)),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='restaurants', to='profiles.profile')),
            ],
        ),
        migrations.CreateModel(
            name='RestaurantVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('date', models.DateField()),
                ('count', models.PositiveIntegerField(default=1, help_text='number of times the user voted for the restaurant on date')),
                ('total', models.FloatField(help_text='total sum of votes made by user for the restaurant on date')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='votes', to='profiles.profile')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='restaurants.restaurant')),
            ],
        ),
        migrations.AddConstraint(
            model_name='restaurant',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_name_case_insensitive'),
        ),
        migrations.AddConstraint(
            model_name='restaurantvote',
            constraint=models.UniqueConstraint(fields=('date', 'profile', 'restaurant'), name='unique_restaurant_vote'),
        ),
    ]
