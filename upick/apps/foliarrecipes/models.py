from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# this is like zinc sulfate
class MineralRaw(models.Model):
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this mineral raw belongs to'
    )
    
    """
    Model to track different mineral sources and their properties
    """
    FORM_CHOICES = [
        ('DRY', 'Dry/Powder'),
        ('LIQUID', 'Liquid'),
    ]

    name = models.CharField(max_length=100, help_text="Name of the raw mineral (e.g., Zinc Sulfate)")
    mineral = models.CharField(max_length=100, help_text="The primary mineral (e.g., Zinc)")
    form = models.CharField(
        max_length=10,
        choices=FORM_CHOICES,
        default='DRY',
        help_text="Physical form of the mineral"
    )
    chemical_formula = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Chemical formula (e.g., ZnSO4)"
    )
    mineral_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of actual mineral content"
    )
    solubility = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Solubility in g/L at 20°C"
    )
    ph_range = models.CharField(
        max_length=50,
        help_text="Optimal pH range for solubility"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about this raw mineral")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.mineral} - {self.mineral_content}% - {self.get_form_display()})"

    def get_best_price(self):
        """Get the best price per unit among all suppliers"""
        products = self.supplier_products.all()
        if products:
            return min(product.price_per_unit() for product in products)
        return None

    class Meta:
        ordering = ['mineral', 'name']
        unique_together = ['name', 'chemical_formula']

class Supplier(models.Model):
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this supplier belongs to'
    )
    
    """
    Model to track suppliers of minerals and other ingredients
    """
    name = models.CharField(max_length=100, help_text="Name of the supplier")
    website = models.URLField(blank=True, help_text="Supplier's website")
    contact_name = models.CharField(max_length=100, blank=True, help_text="Contact person name")
    contact_email = models.EmailField(blank=True, help_text="Contact email address")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    shipping_notes = models.TextField(blank=True, help_text="Notes about shipping options and costs")
    account_number = models.CharField(max_length=50, blank=True, help_text="Your account number with this supplier")
    notes = models.TextField(blank=True, help_text="Additional notes about this supplier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class SupplierMineralProduct(models.Model):
    """
    Model to track mineral products available from suppliers
    """
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this chelated mineral belongs to'
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='mineral_products')
    mineral_raw = models.ForeignKey(MineralRaw, on_delete=models.CASCADE, related_name='supplier_products')
    product_code = models.CharField(max_length=50, blank=True, help_text="Supplier's product code or SKU")
    package_size = models.DecimalField(
        default=1,
        max_digits=8,
        decimal_places=2,
        help_text="Size of the package"
    )
    package_unit = models.CharField(
        default='g',
        max_length=20,
        help_text="Unit of measurement (e.g., kg, L)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per package"
    )
    minimum_order = models.PositiveIntegerField(
        default=1,
        help_text="Minimum order quantity"
    )
    url = models.URLField(
        blank=True,
        help_text="Direct URL to product page"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about this product")
    last_price_update = models.DateField(
        auto_now=True,
        help_text="When the price was last updated"
    )

    def __str__(self):
        return f"{self.mineral_raw.name} from {self.supplier.name} ({self.package_size} {self.package_unit})"

    def price_per_unit(self):
        """Calculate price per unit (g or ml)"""
        return self.price / self.package_size

    class Meta:
        ordering = ['supplier', 'mineral_raw']
        unique_together = ['supplier', 'mineral_raw', 'package_size', 'package_unit']

# this is like citric acid
class ChelatingAgent(models.Model):
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this chelating agent belongs to'
    )
    
    """
    Model to track different chelating agents and their properties
    """
    FORM_CHOICES = [
        ('DRY', 'Dry/Powder'),
        ('LIQUID', 'Liquid'),
    ]

    name = models.CharField(max_length=100, help_text="Name of the chelating agent (e.g., Citric Acid)")
    form = models.CharField(
        max_length=10,
        choices=FORM_CHOICES,
        default='DRY',
        help_text="Physical form of the chelating agent"
    )
    chemical_formula = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Chemical formula"
    )
    optimal_ph_range = models.CharField(
        max_length=50,
        help_text="Optimal pH range for chelation"
    )
    solubility = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Solubility in g/L at 20°C"
    )
    stability_notes = models.TextField(
        blank=True,
        help_text="Notes about stability with different minerals"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about this chelating agent")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_form_display()})"

    class Meta:
        ordering = ['name']
        
class SupplierChelatingProduct(models.Model):
    """
    Model to track chelating agent products available from suppliers
    """
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this chelated mineral belongs to'
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='chelating_products')
    chelating_agent = models.ForeignKey(ChelatingAgent, on_delete=models.CASCADE, related_name='supplier_products')
    product_code = models.CharField(max_length=50, blank=True, help_text="Supplier's product code or SKU")
    package_size = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Size of the package"
    )
    package_unit = models.CharField(
        max_length=20,
        help_text="Unit of measurement (e.g., kg, L)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per package"
    )
    minimum_order = models.PositiveIntegerField(
        default=1,
        help_text="Minimum order quantity"
    )
    url = models.URLField(
        blank=True,
        help_text="Direct URL to product page"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about this product")
    last_price_update = models.DateField(
        auto_now=True,
        help_text="When the price was last updated"
    )

    def __str__(self):
        return f"{self.chelating_agent.name} from {self.supplier.name} ({self.package_size} {self.package_unit})"

    def price_per_unit(self):
        """Calculate price per unit (g or ml)"""
        return self.price / self.package_size

    class Meta:
        ordering = ['supplier', 'chelating_agent']
        unique_together = ['supplier', 'chelating_agent', 'package_size', 'package_unit']


# this is the end chelated mineral like chelated Calciu,
class ChelatedMineral(models.Model):
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this chelated mineral belongs to'
    )
    
    """
    Model to track chelated mineral recipes based on John Kempf's teachings
    """
    name = models.CharField(max_length=100, help_text="Name of the chelated mineral solution")
    mineral_raw = models.ForeignKey(
        MineralRaw,
        on_delete=models.PROTECT,
        help_text="Source of the mineral"
    )
    mineral_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Amount of mineral source in grams"
    )
    water_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Amount of water in liters"
    )
    ph_target = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        help_text="Target pH for chelation"
    )
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Temperature in Celsius for the chelation process"
    )
    chelating_agent = models.ForeignKey(
        ChelatingAgent,
        on_delete=models.PROTECT,
        help_text="Chelating agent used"
    )
    chelating_agent_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Amount of chelating agent in grams"
    )
    process = models.TextField(help_text="Step by step process for creating the chelated mineral")
    notes = models.TextField(blank=True, help_text="Additional notes or observations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.mineral_raw.mineral} chelated with {self.chelating_agent.name}"

    class Meta:
        ordering = ['mineral_raw__mineral', 'name']

class RecipeIngredient(models.Model):
    """
    Model to track ingredients in foliar recipes
    """
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this ingredient belongs to'
    )
    name = models.CharField(max_length=100, help_text="Name of the ingredient")
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Amount of ingredient"
    )
    unit = models.CharField(
        max_length=20,
        help_text="Unit of measurement (e.g., ml, g, L)"
    )
    purpose = models.TextField(
        help_text="Purpose of this ingredient in the recipe"
    )
    optional = models.BooleanField(
        default=False,
        help_text="Whether this ingredient is optional"
    )
    order = models.PositiveIntegerField(
        help_text="Order in which to add this ingredient"
    )

    def __str__(self):
        return f"{self.amount} {self.unit} {self.name}"

    class Meta:
        ordering = ['order']

class FoliarRecipe(models.Model):
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this foliar recipe belongs to'
    )
    
    """
    Model to track foliar spray recipes based on John Kempf's teachings
    """
    GROWTH_STAGES = [
        ('VEG', 'Vegetative'),
        ('FLW', 'Flowering'),
        ('FRT', 'Fruiting'),
        ('ALL', 'All Stages')
    ]

    name = models.CharField(max_length=100, help_text="Name of the foliar spray recipe")
    description = models.TextField(help_text="Purpose and benefits of this foliar spray")
    growth_stage = models.CharField(
        max_length=3,
        choices=GROWTH_STAGES,
        default='ALL',
        help_text="Plant growth stage when this spray is most effective"
    )
    base_water_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Base amount of water in liters"
    )
    target_ph = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        help_text="Target pH for the final solution"
    )
    application_frequency = models.CharField(
        max_length=100,
        help_text="How often to apply (e.g., 'Weekly', 'Every 14 days')"
    )
    best_time = models.CharField(
        max_length=100,
        default='Evening',
        help_text="Best time of day to apply"
    )
    process = models.TextField(help_text="Step by step mixing and application process")
    notes = models.TextField(blank=True, help_text="Additional notes or observations")
    ingredients = models.ManyToManyField(
        RecipeIngredient,
        through='RecipeIngredientRelationship',
        related_name='recipes',
        help_text="Ingredients in this recipe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_growth_stage_display()})"

    class Meta:
        ordering = ['name']

class RecipeIngredientRelationship(models.Model):
    """
    Model to track the relationship between recipes and ingredients
    """
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this relationship belongs to'
    )
    recipe = models.ForeignKey(
        FoliarRecipe,
        on_delete=models.CASCADE,
        related_name='ingredient_relationships'
    )
    ingredient = models.ForeignKey(
        RecipeIngredient,
        on_delete=models.CASCADE,
        related_name='recipe_relationships'
    )
    order = models.PositiveIntegerField(
        help_text="Order in which to add this ingredient to this recipe"
    )

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"

    class Meta:
        ordering = ['recipe', 'order']
        unique_together = ['recipe', 'ingredient']

class PurchasedProduct(models.Model):
    """
    Model to track purchased products and inventory
    """
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this purchased product belongs to'
    )
    supplier_product = models.ForeignKey(
        SupplierMineralProduct,
        on_delete=models.PROTECT,
        related_name='purchases',
        help_text="The product that was purchased"
    )
    purchase_date = models.DateField(help_text="Date of purchase")
    quantity = models.PositiveIntegerField(help_text="Number of packages purchased")
    package_size = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Size of each package"
    )
    package_unit = models.CharField(
        max_length=20,
        help_text="Unit of measurement (e.g., kg, L)"
    )
    price_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Actual price paid per package"
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total shipping cost for this purchase"
    )
    lot_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lot or batch number"
    )
    expiration_date = models.DateField(
        null=True,
        blank=True,
        help_text="Product expiration date"
    )
    remaining_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Remaining quantity in original units"
    )
    storage_location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Where this product is stored"
    )
    purchase_order = models.CharField(
        max_length=50,
        blank=True,
        help_text="Purchase order number"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this purchase"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.supplier_product.mineral_raw.name} - {self.package_size}{self.package_unit} - Purchased {self.purchase_date}"

    def total_cost(self):
        """Calculate total cost including shipping"""
        return (self.price_paid * self.quantity) + self.shipping_cost

    def cost_per_unit(self):
        """Calculate actual cost per unit including shipping"""
        total_units = self.quantity * self.package_size
        return self.total_cost() / total_units if total_units else 0

    def total_quantity(self):
        """Calculate total quantity purchased"""
        return self.quantity * self.package_size

    def is_low_stock(self):
        """Check if remaining quantity is below 20% of original purchase"""
        original_total = self.quantity * self.package_size
        return self.remaining_quantity < (original_total * 0.2)

    def save(self, *args, **kwargs):
        # If this is a new purchase, set the initial remaining quantity
        if not self.pk and self.remaining_quantity is None:
            self.remaining_quantity = self.total_quantity()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-purchase_date', 'supplier_product']
        verbose_name = "Purchased Product"
        verbose_name_plural = "Purchased Products"

class FoliarApplication(models.Model):
    """
    Model to track when foliar recipes are applied
    """
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this foliar application belongs to'
    )
    recipe = models.ForeignKey(
        FoliarRecipe,
        on_delete=models.PROTECT,
        related_name='applications',
        help_text="The recipe that was applied"
    )
    application_date = models.DateField(help_text="Date of application")
    application_time = models.TimeField(help_text="Time of application")
    weather_conditions = models.TextField(
        blank=True,
        help_text="Weather conditions during application (temp, humidity, wind, etc.)"
    )
    area_treated = models.CharField(
        max_length=200,
        help_text="Description of area where recipe was applied"
    )
    actual_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Actual amount applied in liters"
    )
    effectiveness_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate effectiveness from 1-5"
    )
    observations = models.TextField(
        blank=True,
        help_text="Observations about application or results"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recipe.name} applied on {self.application_date}"

    class Meta:
        ordering = ['-application_date', '-application_time']
        verbose_name = "Foliar Application"
        verbose_name_plural = "Foliar Applications"

class FoliarSchedule(models.Model):
    """
    Model to schedule future foliar spray applications
    """
    group = models.ForeignKey(
       Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The group this foliar schedule belongs to'
    )
    REPEAT_CHOICES = [
        ('NONE', 'One-time'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Every 2 weeks'),
        ('MONTHLY', 'Monthly'),
        ('CUSTOM', 'Custom days'),
    ]

    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('COMPLETED', 'Completed'),
        ('SKIPPED', 'Skipped'),
        ('CANCELLED', 'Cancelled'),
    ]

    recipe = models.ForeignKey(
        FoliarRecipe,
        on_delete=models.PROTECT,
        related_name='schedules',
        help_text="The recipe to be applied"
    )
    start_date = models.DateField(help_text="Start date of the schedule")
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional end date of the schedule"
    )
    preferred_time = models.TimeField(help_text="Preferred time of day for application")
    repeat_pattern = models.CharField(
        max_length=10,
        choices=REPEAT_CHOICES,
        default='NONE',
        help_text="How often to repeat the application"
    )
    custom_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of days between applications if using custom repeat pattern"
    )
    area_to_treat = models.CharField(
        max_length=200,
        help_text="Description of area to be treated"
    )
    planned_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Planned amount to apply in liters"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PLANNED',
        help_text="Current status of the scheduled application"
    )
    weather_requirements = models.TextField(
        blank=True,
        help_text="Specific weather conditions required (temp range, wind speed, etc.)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this scheduled application"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recipe.name} scheduled for {self.start_date}"

    def next_application_date(self):
        """Calculate the next application date based on the repeat pattern"""
        if self.status != 'PLANNED':
            return None
            
        last_application = self.applications.order_by('-application_date').first()
        base_date = last_application.application_date if last_application else self.start_date
        
        if self.repeat_pattern == 'NONE':
            return base_date
        elif self.repeat_pattern == 'DAILY':
            return base_date + timedelta(days=1)
        elif self.repeat_pattern == 'WEEKLY':
            return base_date + timedelta(weeks=1)
        elif self.repeat_pattern == 'BIWEEKLY':
            return base_date + timedelta(weeks=2)
        elif self.repeat_pattern == 'MONTHLY':
            return base_date + relativedelta(months=1)
        elif self.repeat_pattern == 'CUSTOM' and self.custom_days:
            return base_date + timedelta(days=self.custom_days)
        return None

    def is_active(self):
        """Check if the schedule is currently active"""
        today = date.today()
        return (
            self.status == 'PLANNED' and
            self.start_date <= today and
            (not self.end_date or self.end_date >= today)
        )

    class Meta:
        ordering = ['start_date', 'preferred_time']
        verbose_name = "Foliar Schedule"
        verbose_name_plural = "Foliar Schedules"
