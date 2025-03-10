from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils import timezone
from apps.plants.models import Variety
from apps.planning.models import SeedInventory
from datetime import timedelta
from apps.produceplanner.models import ProducePlanOverview

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
    produce_plan = models.ForeignKey(
        ProducePlanOverview,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The produce plan this planting schedule belongs to'
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


class TodoList(models.Model):
    """Model representing a collection of related tasks"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this list belongs to'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_completion_percentage(self):
        """Calculate the percentage of completed tasks in this list"""
        total_tasks = TodoTask.objects.filter(task=self).count()
        if total_tasks == 0:
            return 0
        completed_tasks = total_tasks.objects.filter(task=self, status='COMPLETED').count()
        return int((completed_tasks / total_tasks) * 100)
    
    class Meta:
        verbose_name = "Todo List"
        verbose_name_plural = "Todo Lists"
        ordering = ['title']


class TodoTask(models.Model):
    """Model representing a single task to be completed"""
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
     
    title = models.CharField(max_length=200)
    tasklist = models.ForeignKey(TodoList, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='TODO')
    garden_bed = models.ForeignKey(GardenBed, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='todo_tasks')
    planting_schedule = models.ForeignKey(PlantingSchedule, on_delete=models.SET_NULL, null=True, blank=True, 
                                         related_name='todo_tasks')
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this task belongs to'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Todo Task"
        verbose_name_plural = "Todo Tasks"
        ordering = ['due_date', 'priority']
