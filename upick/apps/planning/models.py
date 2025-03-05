from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from apps.plants.models import Plant
from django.core.exceptions import ValidationError

class SeedSource(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, help_text='The group this seed source belongs to')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class SeedInventory(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    source = models.ForeignKey(SeedSource, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, help_text='The group this seed inventory belongs to')
    purchase_date = models.DateField()
    lot_number = models.CharField(max_length=50, blank=True)
    packet_size = models.CharField(max_length=50, help_text="Size or weight of the seed packet")
    seeds_per_packet = models.IntegerField(null=True, blank=True, help_text="Approximate number of seeds")
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    germination_rate = models.IntegerField(null=True, blank=True, help_text="Known germination rate percentage")
    germination_test_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    seeds_remaining = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plant.name} - {self.source.name} ({self.purchase_date})"

    class Meta:
        ordering = ['-purchase_date', 'plant__name']
        verbose_name_plural = "Seed inventories"

class SeedSourceDocument(models.Model):
    """
    Model to store documents related to seed sources.
    """
    file = models.FileField(upload_to='documents/seed_sources/')
    short_description = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    seed_source = models.ForeignKey('SeedSource', on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.file.name} - {self.pk}'

class GardenConfiguration(models.Model):
    # Garden Bed Defaults
    default_bed_length = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Default length for new garden beds (feet)"
    )
    default_bed_width = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Default width for new garden beds (feet)"
    )
    
    # Growing Season
    spring_frost_date = models.DateField(
        help_text="Average last frost date in spring"
    )
    fall_frost_date = models.DateField(
        help_text="Average first frost date in fall"
    )
    growing_zone = models.CharField(
        max_length=10,
        help_text="USDA growing zone (e.g., '6b')",
        blank=True
    )
    
    # Location
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Garden latitude for sun calculations"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Garden longitude for sun calculations"
    )
    
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this garden configuration belongs to'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and GardenConfiguration.objects.exists():
            raise ValidationError('There can be only one GardenConfiguration instance')
        return super(GardenConfiguration, self).save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        config = cls.objects.first()
        if config is None:
            config = cls.objects.create(
                default_bed_length=100.0,
                default_bed_width=3.0,
                spring_frost_date=settings.SPRING_FROST_DATE if hasattr(settings, 'SPRING_FROST_DATE') else None,
                fall_frost_date=settings.FALL_FROST_DATE if hasattr(settings, 'FALL_FROST_DATE') else None
            )
        return config

    class Meta:
        verbose_name = "Garden Configuration"
        verbose_name_plural = "Garden Configuration"

class GardenPlan(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, help_text='The group this garden plan belongs to')
    year = models.IntegerField()
    start_date = models.DateField(null=True, blank=True, help_text="When to start implementing this plan")
    end_date = models.DateField(null=True, blank=True, help_text="When this plan should be completed")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.year})"

    class Meta:
        ordering = ['year', 'name']
        unique_together = ['group', 'name', 'year']

class CropRotationRule(models.Model):
    plant_family = models.CharField(max_length=100)
    years_before_repeat = models.IntegerField(default=3)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this crop rotation rule belongs to'
    )

    class Meta:
        ordering = ['plant_family']
