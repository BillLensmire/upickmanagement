from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group
from apps.plants.models import Plant
from apps.beneficials.models import Beneficial
from apps.planning.models import SeedSource
from apps.foliarrecipes.models import FoliarRecipe
from apps.schedule.models import GardenBed
from datetime import date
from apps.produceplanner.models import ProducePlanOverview

class LogEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('PLANTS', 'Plants'),
        ('FRUIT_TREE', 'Fruit Tree'),
        ('VEGETABLE', 'Vegetable'),
        ('FRUITE_BUSHES', 'Fruit Bushes'),
        ('NOTES_NEXT_YEAR', 'Notes for Next Year'),
        ('FOLIAR', 'Foliar'),
        ('COVER_CROP', 'Cover Crop'),
        ('BENEFICIAL', 'Beneficial'),
        ('PRODUCE_PLANNER', 'Produce Planner'),
        ('SCHEDULE', 'Schedule'),
        ('GENERAL', 'General'),
        ('HARVEST', 'Harvest'),
        ('GARDEN_BED', 'Garden Bed'),
        ('SEED_SOURCE', 'Seed Source'),
        ('CUTTINGS', 'Cuttings')
    ]

    # Basic fields
    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPE_CHOICES,
        help_text='Type of log entry'
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Title of the log entry'
    )
    logdate = models.DateField(
        default=date.today,
        help_text='Date of the log entry'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Main text content of the log entry'
    )

    # LaTeX support
    description_includes_latex = models.BooleanField(
        default=False,
        help_text='Indicates if the description includes LaTeX'
    )

    # Optional file fields
    photo = models.ImageField(
        upload_to='photos/log_photos/', 
        blank=True,
        null=True,
        help_text='Optional photo attachment'
    )
    document = models.FileField(
        upload_to='documents/log_documents/',
        blank=True,
        null=True,
        help_text='Optional document attachment'
    )
    
    # Group association
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this log entry belongs to'
    )

    # Optional references to other models
    plants = models.ManyToManyField(
        Plant,
        blank=True,
        related_name='log_entries',
        help_text='Related plants'
    )
    plant_schedule = models.ForeignKey(
        ProducePlanOverview,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='log_entries',
        help_text='Related plant schedule'
    )
    foliar_recipe = models.ForeignKey(
        FoliarRecipe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='log_entries',
        help_text='Related foliar recipe'
    )
    cover_crop = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cover_crop_log_entries',
        help_text='Related cover crop'
    )
    beneficial = models.ForeignKey(
        Beneficial,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='log_entries',
        help_text='Related beneficial organism'
    )
    garden_bed = models.ForeignKey(
        GardenBed,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='log_entries',
        help_text='Related garden bed'
    )
    seed_source = models.ForeignKey(
        SeedSource,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='log_entries',
        help_text='Related seed source'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Log Entry'
        verbose_name_plural = 'Log Entries'
        ordering = ['-logdate']

    def __str__(self):
        if self.logdate:
            ldate = self.logdate.strftime("%Y-%m-%d %H:%M")
        else:
            ldate = "N/A"
        return f'{self.get_entry_type_display()} - {ldate}'
