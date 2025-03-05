from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group

class Beneficial(models.Model):
    TYPE_CHOICES = [
        ('INSECT', 'Insect'),
        ('BIRD', 'Bird'),
        ('ANIMAL', 'Animal'),
    ]

    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]

    name = models.CharField(max_length=100, help_text='Common name of the beneficial organism')
    species = models.CharField(max_length=100, blank=True, help_text='Scientific name/species of the beneficial')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, help_text='Category of beneficial organism')
    
    # Seasonal presence
    active_from_month = models.IntegerField(
        choices=MONTH_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text='Month when the beneficial typically becomes active.'
    )
    active_to_month = models.IntegerField(
        choices=MONTH_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text='Month when the beneficial typically becomes inactive'
    )
    
    benefits = models.TextField(help_text='Description of how this organism benefits the garden')
    photo = models.ImageField(
        upload_to='photos/beneficials/',
        blank=True,
        null=True,
        help_text='Photo of the beneficial organism'
    )
    
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this beneficial organism belongs to'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Beneficial Organism'
        verbose_name_plural = 'Beneficial Organisms'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'
