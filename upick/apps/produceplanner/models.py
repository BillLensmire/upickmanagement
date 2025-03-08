from django.db import models
from django.contrib.auth.models import Group
from apps.plants.models import Plant, Variety

class ProducePlanOverview(models.Model):
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this produce plan overview belongs to'
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    overall_start_date = models.DateField(
        help_text="First date produce can be available for Picking"
    )
    overall_end_date = models.DateField(
        help_text="Last date produce can be available for Picking"
    )
    year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Overview for {self.name} {self.year}"

    class Meta:
        verbose_name = "You Pick Year Setting"
        verbose_name_plural = "You Pick Year Settings"

class ProducePlan(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    variety = models.ForeignKey(
        Variety, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text='The specific variety of the plant'
    )
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
       null=True,
        blank=True,
        help_text='The group this produce plan belongs to'
    )
    produce_plan_overview = models.ForeignKey(ProducePlanOverview, on_delete=models.CASCADE, related_name='produce_plans', null=True, blank=True)
    
    def __str__(self):
        variety_str = f" ({self.variety.variety_name})" if self.variety else ""
        return f"{self.plant.name}{variety_str} - {self.produce_plan_overview.name}"

    class Meta:
        verbose_name = "You Pick Produce List"
        verbose_name_plural = "You Pick Produce Lists"