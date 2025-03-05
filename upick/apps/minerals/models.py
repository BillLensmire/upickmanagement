from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group

# Create your models here.

class MineralNutrient(models.Model):
    """Model for recording information about minerals and micronutrients needed for plant growth."""
    
    # Nutrient Categories
    CATEGORY_CHOICES = [
        ('macronutrient', 'Macronutrient'),
        ('micronutrient', 'Micronutrient'),
        ('secondary', 'Secondary Nutrient'),
        ('other', 'Other')
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, help_text="Name of the mineral or nutrient")
    symbol = models.CharField(max_length=5, blank=True, help_text="Chemical symbol if applicable (e.g., N, P, K)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='micronutrient', 
                              help_text="Category of nutrient")
    description = models.TextField(blank=True, help_text="General description of the nutrient")
    
    # Plant Health Information
    function = models.TextField(blank=True, help_text="Function of this nutrient in plant growth")
    deficiency_symptoms = models.TextField(blank=True, help_text="Signs of deficiency in plants")
    excess_symptoms = models.TextField(blank=True, help_text="Signs of excess/toxicity in plants")
    
    # Soil and Application Information
    optimal_soil_ph = models.CharField(max_length=50, blank=True, 
                                     help_text="Optimal soil pH range for availability")
    sources = models.TextField(blank=True, 
                             help_text="Natural and commercial sources of this nutrient")
    application_methods = models.TextField(blank=True, 
                                        help_text="Recommended application methods")
    application_rate = models.CharField(max_length=255, blank=True, 
                                      help_text="Typical application rates")
    
    # Interactions
    interactions = models.TextField(blank=True, 
                                  help_text="Interactions with other nutrients (synergistic or antagonistic)")
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this mineral/nutrient belongs to'
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Mineral/Nutrient"
        verbose_name_plural = "Minerals & Nutrients"
    
    def __str__(self):
        return self.name


class PlantNutrientRequirement(models.Model):
    """Model for recording specific nutrient requirements for different plants."""
    
    # Requirement Levels
    REQUIREMENT_LEVEL = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('variable', 'Variable/Depends on Growth Stage')
    ]

    CATEGORY_CRITICAL_POINTS_OF_INFLUENCE = [
        ('GERMINATION', 'Germination'),
        ('REPRODUCTIVE_BUD_INITIATION', 'Reproductive Bud Initiation'),
        ('BLOSSOMING_POLLINATION', 'Blossoming/Pollination'),
        ('FRUIT_FILL', 'Fruit Fill'),
        ('SENESCENCE', 'Senescence')
    ]
    
    plant_type = models.CharField(max_length=100, help_text="Type of plant or crop")
    nutrient = models.ForeignKey(MineralNutrient, on_delete=models.CASCADE, 
                                related_name='plant_requirements')
    requirement_level = models.CharField(max_length=20, choices=REQUIREMENT_LEVEL, 
                                       help_text="Level of requirement for this nutrient")
    notes = models.TextField(blank=True, 
                           help_text="Specific notes about this plant's requirements for this nutrient")
        
    critical_points_of_influence = models.CharField(max_length=30, choices=CATEGORY_CRITICAL_POINTS_OF_INFLUENCE, blank=True, 
                                                    help_text="Critical points of influence in plant growth")
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this plant mineral/nutrient belongs to'
    )

    class Meta:
        ordering = ['plant_type', 'nutrient__name']
        verbose_name = "Plant Nutrient Requirement"
        verbose_name_plural = "Plant Nutrient Requirements"
        unique_together = ['plant_type', 'nutrient']
    
    def __str__(self):
        return f"{self.plant_type} - {self.nutrient.name}"


class NutrientNote(models.Model):
    """Model for recording general notes and observations about nutrients."""
    
    title = models.CharField(max_length=200, help_text="Title of the note")
    nutrient = models.ForeignKey(MineralNutrient, on_delete=models.CASCADE, 
                                related_name='notes', null=True, blank=True,
                                help_text="Related nutrient (optional)")
    content = models.TextField(help_text="Note content")
    source = models.CharField(max_length=255, blank=True, 
                            help_text="Source of information (book, website, personal observation)")
  
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this nutrient note belongs to'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Nutrient Note"
        verbose_name_plural = "Nutrient Notes"
    
    def __str__(self):
        return self.title

class MineralUrl(models.Model):
    """Model for recording URLs related to minerals."""
    
    mineral = models.ForeignKey(MineralNutrient, on_delete=models.CASCADE, 
                                related_name='urls', null=True, blank=True,
                                help_text="Related mineral (optional)")
    url = models.URLField()
  
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mineral URL"
        verbose_name_plural = "Mineral URLs"
    
    def __str__(self):
        return self.mineral.name + " - " + self.url