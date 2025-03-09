from django.db import models
from django.contrib.auth.models import Group

class Plant(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this plant belongs to'
    )
    description = models.TextField(blank=True)
    research_notes = models.TextField(blank=True, null=True)
    
    # Plant type
    seed_type = models.CharField(
        max_length=20,
        choices=[
            ('VEGETABLE', 'Vegetable'),
            ('FLOWER', 'Flower'),
            ('FRUIT TREE', 'Fruit Tree'),
            ('COVER CROP', 'Cover Crop'),
            ('HERB', 'Herb'),
            ('PERENNIAL', 'Perennial'),
            ('CORN', 'Corn')
        ],
        default='VEGETABLE'
    )

    # the following fields are common to a variety and a plant
    #    will supply default values to the variety
    # Planting specifications
    planting_method = models.CharField(
        max_length=20,
        choices=[
            ('DIRECT', 'Direct Seed'),
            ('TRANSPLANT', 'Transplant')
        ],
        default='DIRECT'
    )
    spacing_between_plants = models.IntegerField(
        help_text="Recommended spacing between plants in inches"
    )
    spacing_between_rows = models.IntegerField(
        help_text="Recommended spacing between rows in inches"
    )
    
    # Temperature and timing
    germination_temp_min = models.IntegerField(
        help_text="Minimum soil temperature for germination (°F)",
        null=True,
        blank=True
    )
    germination_temp_max = models.IntegerField(
        help_text="Maximum soil temperature for germination (°F)",
        null=True,
        blank=True
    )
    days_to_germinate = models.IntegerField(
        help_text="Average days from sowing to germination",
        null=True,
        blank=True
    )
    days_to_maturity = models.IntegerField(
        help_text="Days from transplant/direct seeding to harvest",
        null=True,
        blank=True
    )
    days_from_seed_to_transplant = models.IntegerField(
        help_text="Days from seed starting to transplanting",
        null=True,
        blank=True
    )
    days_from_frost_to_transplant = models.IntegerField(
        help_text="Number of days after last frost date to transplant",
        null=True,
        blank=True
    )
    number_of_harvest_days = models.IntegerField(default=60,help_text="Number of expected days to harvest this produce.")
    
    # Plant characteristics
    height_inches = models.IntegerField(help_text="Average height at maturity in inches")
    
    # Additional info
    is_perennial = models.BooleanField(default=False)
    companion_plants = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']



# A variety belongs to a plant and where the fields have similar names, the Plant will
#   supply the default values
class Variety(models.Model):
    variety_plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The variety for a plant'
    )
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this variety belongs to'
    )
    variety_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, blank=True)
    variety_description = models.TextField(blank=True)

    # Planting specifications
    variety_planting_method = models.CharField(
        max_length=20,
        choices=[
            ('DIRECT', 'Direct Seed'),
            ('TRANSPLANT', 'Transplant'),
            ('ROOT_DIVIDING', 'Root Dividing'),
            ('CUTTINGS', 'Cuttings')
        ],
        default='DIRECT'
    )
    variety_spacing_between_plants = models.IntegerField(
        help_text="Recommended spacing between plants in inches",
        null=True,
        blank=True
    )
    variety_spacing_between_rows = models.IntegerField(
        help_text="Recommended spacing between rows in inches",
        null=True,
        blank=True
    )
    variety_days_to_maturity = models.IntegerField(
        help_text="Days from transplant/direct seeding to harvest",
        null=True,
        blank=True
    )
    variety_days_from_seed_to_transplant = models.IntegerField(
        help_text="Days from seed starting to transplanting",
        null=True,
        blank=True
    )
    variety_days_from_frost_to_transplant = models.IntegerField(
        help_text="Number of days after last frost date to transplant",
        null=True,
        blank=True
    )
    number_of_harvest_days = models.IntegerField(default=60,help_text="Number of expected days to harvest this produce.")
    # Seasonal timing
    variety_planting_season = models.CharField(
        max_length=20,
        choices=[
            ('SPRING', 'Spring'),
            ('SUMMER', 'Summer'),
            ('FALL', 'Fall'),
            ('WINTER', 'Winter')
        ],
        default='SPRING'
    )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.variety_name}"

    class Meta:
        ordering = ['variety_name']