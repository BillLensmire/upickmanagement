from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group
from apps.planning.models import SeedInventory, Plant
from apps.beneficials.models import Beneficial

class CoverCropMix(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this cover crop mix belongs to'
    )
    description = models.TextField(blank=True)
    seeds2 = models.ManyToManyField(SeedInventory, through='CoverCropPlantComponent')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CoverCropPlantComponent(models.Model):
    mix = models.ForeignKey(CoverCropMix, on_delete=models.CASCADE, null=True, blank=True, help_text='The mix this plant component belongs to')
    seed_inventory = models.ForeignKey(SeedInventory, on_delete=models.CASCADE, null=True, blank=True, help_text='The seed inventory this component uses')
    seeding_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Seeding rate in lbs/acre",
        validators=[MinValueValidator(0)]
    )
    percentage_in_mix = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percentage of this seed in the mix"
    )

    class Meta:
        unique_together = ['mix', 'seed_inventory']

class CoverCropPlan(models.Model):
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this cover crop plan belongs to'
    )
    
    TERMINATION_METHODS = [
        ('TILL', 'Till In'),
        ('MOWING', 'Mowing'),
        ('WINTER_KILL', 'Winter Kill'),
        ('ROLLER_CRIMPER', 'Roller Crimper'),
        ('HERBICIDE', 'Herbicide')
    ]

    SEASON_CHOICES = [
        ('SPRING', 'Spring'),
        ('SUMMER', 'Summer'),
        ('FALL', 'Fall'),
        ('WINTER', 'Winter')
    ]

    mix = models.ForeignKey(CoverCropMix, on_delete=models.CASCADE, null=True, blank=True, help_text='The mix this cover crop plan belongs to')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Timing
    planting_season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    planting_window_start = models.DateField(help_text="When to start planting")
    planting_window_end = models.DateField(help_text="Last date for planting")
    weeks_to_grow = models.IntegerField(help_text="Weeks to grow before termination")
    
    # Growing conditions
    minimum_soil_temp = models.IntegerField(
        help_text="Minimum soil temperature for planting (°F)",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    frost_tolerant = models.BooleanField(default=False)
    drought_tolerant = models.BooleanField(default=False)
    
    # Benefits and management
    nitrogen_fixer = models.BooleanField(default=False,
        help_text="Indicates if this cover crop is a nitrogen fixer"
    )
    biomass_producer = models.BooleanField(default=False,
        help_text="Indicates if this cover crop is a biomass producer"
    )
    weed_suppressor = models.BooleanField(default=False,
        help_text="Indicates if this cover crop is a weed suppressant"
    )
    erosion_controller = models.BooleanField(default=False,
        help_text="Indicates if this cover crop is an erosion controller"
    )
    beneficial_insect = models.BooleanField(
        default=False,
        help_text="Indicates if this cover crop attracts beneficial insects"
    )
    attracted_beneficials = models.ManyToManyField(
        Beneficial,
        blank=True,
        help_text="Specific beneficial organisms attracted to this cover crop",
        related_name='cover_crop_plans'
    )
    
    # Termination
    termination_method = models.CharField(
        max_length=20,
        choices=TERMINATION_METHODS,
        help_text="Recommended method for terminating the cover crop"
    )
    days_before_cash_crop = models.IntegerField(
        help_text="Days to terminate before planting next crop",
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('covercrops:plan_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name} - {self.planting_season}"
