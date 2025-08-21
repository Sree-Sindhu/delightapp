from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .utils.email_service import EmailService

class Store(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True) # blank=True makes it optional

    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    

    def __str__(self):
        return self.name
    
# A new model for cake categories
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# A new model for user reviews
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    cake = models.ForeignKey('Cake', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.cake.name} by {self.user.username}"
    
class Cake(models.Model):
    name = models.CharField(max_length=100)
    flavor = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='cakes')
    price = models.DecimalField(max_digits=6, decimal_places=2)

    stores = models.ManyToManyField('Store', related_name='cakes')

    def __str__(self):
        return self.name

# A new model for user reviews of stores
class StoreReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_reviews')
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='store_reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.store.name} by {self.user.username}"
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    flat_number = models.CharField(max_length=20, blank=True)
    building_name = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=100)
    area_or_colony = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.city}, {self.pincode}"


class DeliveryAgent(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # for tracking

    def __str__(self):
        return f"{self.name} ({self.phone})"
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    cake = models.ForeignKey('Cake', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    customization = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cake.name} ({self.quantity})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    agent = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Order.objects.get(pk=self.pk)
            if original.status != self.status:
                OrderStatusHistory.objects.create(order=self, status=self.status)
        else:
            super().save(*args, **kwargs)
            OrderStatusHistory.objects.create(order=self, status=self.status)
            return # This return ensures the second super().save() is not called on initial creation
        super().save(*args, **kwargs)


@receiver(post_save, sender=Order)
def order_email_notifications(sender, instance: 'Order', created: bool, **kwargs):
    """Send emails on order creation and when marked delivered."""
    user = instance.user
    to_email = getattr(user, 'email', None)
    if not to_email:
        return

    try:
        if created:
            EmailService.send_order_received(user, instance)
        else:
            if instance.status == 'delivered':
                EmailService.send_order_delivered(user, instance)
    except Exception:
        pass

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    cake = models.ForeignKey('Cake', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.cake.name}"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey('Order', related_name='status_history', on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.id} - {self.status} @ {self.timestamp}"
    
class OrderAlert(models.Model):
    ALERT_CHOICES = [
        ('delayed', 'Delayed'),
        ('issue', 'Issue'),
        ('cancelled_by_store', 'Cancelled by Store'),
    ]

    order = models.ForeignKey('Order', related_name='alerts', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50, choices=ALERT_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.id} - {self.alert_type}"
    

class CustomerProfile(models.Model):
    GENDER_CHOICES = (
        ('-', '-'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return self.user.username


# --- Simple deterministic geocoder to avoid external API ---
def _fake_geocode(addr: str, city_hint: str = ""):
    base_map = {
        'Bengaluru': (12.9716, 77.5946),
        'Hyderabad': (17.3850, 78.4867),
        'Mumbai': (19.0760, 72.8777),
        'Delhi': (28.6139, 77.2090),
    }
    base = base_map.get(city_hint or '', (17.3850, 78.4867))
    h = abs(hash(addr)) % 10000
    dlat = ((h % 200) - 100) / 10000.0
    dlon = (((h // 200) % 200) - 100) / 10000.0
    return base[0] + dlat, base[1] + dlon


@receiver(pre_save, sender=Store)
def store_autogeocode(sender, instance: 'Store', **kwargs):
    if instance and instance.location and (not instance.latitude or not instance.longitude):
        # Try to infer city as last token or known cities present
        city_hint = None
        for c in ['Bengaluru', 'Hyderabad', 'Mumbai', 'Delhi']:
            if c.lower() in instance.location.lower():
                city_hint = c
                break
        lat, lon = _fake_geocode(instance.location, city_hint or '')
        instance.latitude = instance.latitude or lat
        instance.longitude = instance.longitude or lon


@receiver(pre_save, sender=Address)
def address_autogeocode(sender, instance: 'Address', **kwargs):
    if instance and (instance.latitude is None or instance.longitude is None):
        addr = f"{instance.flat_number} {instance.building_name} {instance.street} {instance.area_or_colony} {instance.city} {instance.state} {instance.pincode}"
        lat, lon = _fake_geocode(addr, instance.city or '')
        instance.latitude = lat
        instance.longitude = lon