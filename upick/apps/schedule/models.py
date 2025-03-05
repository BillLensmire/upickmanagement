from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from apps.plants.models import Plant, Variety
from apps.planning.models import GardenPlan, SeedInventory
from datetime import timedelta

# Create your models here.

class GardenBed(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this garden bed belongs to'
    )
    width_feet = models.DecimalField(max_digits=5, decimal_places=2)
    length_feet = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    year = models.IntegerField(
        null=True,
        blank=True,
        help_text='The year this garden bed is being used')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.width_feet}' x {self.length_feet}')"

    class Meta:
        ordering = ['name']

class PlantingSchedule(models.Model):
    garden_bed = models.ForeignKey(GardenBed, on_delete=models.CASCADE)
    variety = models.ForeignKey(Variety, null=True, blank=True, on_delete=models.CASCADE)
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this planting schedule belongs to'
    )
    garden_plan = models.ForeignKey(
        GardenPlan,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The garden plan this planting schedule belongs to'
    )
    seed_inventory = models.ForeignKey(SeedInventory, on_delete=models.SET_NULL, null=True, blank=True)
    inside_planting_date = models.DateField(null=True, blank=True, help_text="Date when the seed will be planted inside.")
    quantity = models.IntegerField(default=1, help_text="Number of seeds or plants")
    rows = models.IntegerField(default=1, help_text="Number of rows to plant in the bed")
    notes = models.TextField(blank=True)
    location_notes = models.TextField(blank=True, help_text="Description of where in the bed this will be planted")
    status = models.CharField(
        max_length=20,
        choices=[
            ('PLANNED', 'Planned'),
            ('PLANTED', 'Planted'),
            ('HARVESTED', 'Harvested'),
            ('FAILED', 'Failed')
        ],
        default='PLANNED'
    )
    outside_planting_date = models.DateField(null=True, blank=True, help_text="Date when the seed/plant will be planted outside the garden")
    harvest_date = models.DateField(null=True, blank=True)
    succession_group = models.IntegerField(default=1, help_text="Group number for succession planting")
    
    # Position in bed (optional)
    x_position = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    y_position = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.variety.variety_name} in {self.garden_bed.name} - {self.inside_planting_date}"

    def calculate_bed_length(self):
        """Calculate the length of bed needed in feet based on plant spacing and number of plants/rows"""
        # First check if variety has spacing defined
        if self.variety.variety_spacing_between_plants:
            spacing = self.variety.variety_spacing_between_plants
        # If not, use the plant's spacing
        elif self.variety.variety_plant and self.variety.variety_plant.spacing_between_plants:
            spacing = self.variety.variety_plant.spacing_between_plants
        else:
            return None
            
        # Convert plant spacing from inches to feet
        spacing_in_feet = spacing / 12.0
        
        # Calculate length needed for one row
        plants_per_row = self.quantity / self.rows
        length_per_row = plants_per_row * spacing_in_feet
        
        # Return the length (rounded up to nearest 0.5 foot)
        return round(length_per_row * 2) / 2

    def calculate_dates_from_harvest(self, target_harvest_date):
        """Calculate planting dates working backwards from target harvest date"""
        # First check if variety has days_to_maturity defined
        if self.variety.variety_days_to_maturity:
            dtm = self.variety.variety_days_to_maturity
        # If not, use the plant's days_to_maturity
        elif self.variety.variety_plant and self.variety.variety_plant.days_to_maturity:
            dtm = self.variety.variety_plant.days_to_maturity
        else:
            dtm = 40 #default
            
        # First check if variety has planting method defined
        if self.variety.variety_planting_method:
            planting_method = self.variety.variety_planting_method
        # If not, use the plant's planting method
        elif self.variety.variety_plant:
            planting_method = self.variety.variety_plant.planting_method
        else:
            planting_method = 'DIRECT'
            
        if planting_method == 'TRANSPLANT':
            # First check if variety has days_from_seed_to_transplant defined
            if self.variety.variety_days_from_seed_to_transplant:
                stt = self.variety.variety_days_from_seed_to_transplant
            # If not, use the plant's days_from_seed_to_transplant
            elif self.variety.variety_plant and self.variety.variety_plant.days_from_seed_to_transplant:
                stt = self.variety.variety_plant.days_from_seed_to_transplant
            else:
                stt = 30 #default
                
            # Calculate outside planting date
            outside_date = target_harvest_date - timedelta(days=dtm)
            # Calculate inside planting date
            inside_date = outside_date - timedelta(days=stt)
            
            return {
                'inside_planting_date': inside_date,
                'outside_planting_date': outside_date,
                'harvest_date': target_harvest_date
            }
        else:  # DIRECT
            # Calculate outside planting date
            outside_date = target_harvest_date - timedelta(days=dtm)
            
            return {
                'inside_planting_date': None,
                'outside_planting_date': outside_date,
                'harvest_date': target_harvest_date
            }
