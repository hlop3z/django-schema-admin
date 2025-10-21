from django.db import models

# Create your models here.
class Person(models.Model):
    # Basic fields
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    bio = models.TextField(blank=True)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    file_attachment = models.FileField(upload_to='files/', null=True, blank=True)
    uuid = models.UUIDField(unique=True, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    
    class Meta:
        verbose_name_plural = "People"

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Product(models.Model):
    # One-to-Many relationship (ForeignKey)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    # Many-to-Many relationship
    tags = models.ManyToManyField('Tag', related_name='products')
    # One-to-One relationship
    details = models.OneToOneField('ProductDetail', on_delete=models.CASCADE, null=True)
    
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class ProductDetail(models.Model):
    sku = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=200)
    # Choices field example
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    # Positive Integer field
    stock = models.PositiveIntegerField(default=0)
    # JSON field
    specifications = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Details for {self.product.name}"

class Order(models.Model):
    # Self-referential ForeignKey
    parent_order = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Person, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, through='OrderItem')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    # Duration field
    processing_time = models.DurationField(null=True)
    
    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    # Through model for Many-to-Many relationship
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"
