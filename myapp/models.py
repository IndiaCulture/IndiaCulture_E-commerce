from django.db import models
from django.conf import settings
import random
from django.utils import timezone
from datetime import timedelta
from myapp.storage import LowQualityCloudinaryStorage
from cloudinary.uploader import destroy
from cloudinary.models import CloudinaryField
from django.core.validators import FileExtensionValidator


# Category model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(storage=LowQualityCloudinaryStorage(), upload_to='category_images/', default='default-category.jpg')

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return ''

# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Added old price
    new_price = models.DecimalField(max_digits=10, decimal_places=2)  # Renamed price to new_price
    offer_line = models.CharField(max_length=255, blank=True, null=True)  # Added offer line
    images = models.ManyToManyField('ProductImage', related_name='products')  # Changed to ManyToMany for multiple images
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_bestsell = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def image_urls(self):
        return [image.image.url for image in self.images.all()]
    @property
    def price(self):
        return self.new_price
    

class ProductImage(models.Model):
    image = models.ImageField(storage=LowQualityCloudinaryStorage(), upload_to='product_images/')
    alt_text = models.CharField(max_length=255)

    def __str__(self):
        return self.alt_text or "Product Image"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_image = ProductImage.objects.get(pk=self.pk).image
                if old_image != self.image:
                    destroy(old_image.public_id)
            except ProductImage.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class Offer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    image = models.ImageField(storage=LowQualityCloudinaryStorage(), upload_to='offer_images/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Offer for {self.product.name}"

# Cart model
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.new_price * self.quantity
    
#Checkout and order
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    order_code = models.CharField(max_length=4, unique=True, blank=True, null=True)
    expected_delivery = models.DateField(blank=True, null=True)
    # razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    # razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    # razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    payment_screenshot = CloudinaryField('Payment Screenshot', blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Set order_code if not already set
        if not self.order_code:
            self.order_code = self._generate_unique_order_code()

        # Set expected delivery (e.g., 5 days from order date)
        if not self.expected_delivery:
            self.expected_delivery = timezone.now().date() + timedelta(days=5)

        super().save(*args, **kwargs)

    def _generate_unique_order_code(self):
        while True:
            code = str(random.randint(1000, 9999))  # Generate a random 4-digit string
            if not Order.objects.filter(order_code=code).exists():
                return code
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store at time of purchase

#Watchlist model
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # prevent duplicate wishlist entries

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
    
# Review model
class Review(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # e.g., 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.rating} Stars"
    
#Social gift model
class SocialOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='social_offers')
    gif = CloudinaryField('video', resource_type='video', null=True, blank=True)  # GIF or short video
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Social Offer for {self.product.name}"