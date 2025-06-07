from django.contrib import admin
from .models import Category, Product, Offer, Cart, CartItem, Order, OrderItem, Wishlist, Review, SocialOffer, ProductImage
from django.utils.html import format_html
from django.contrib import messages

# Category, Product, Offer
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'new_price', 'stock', 'is_active', 'is_bestsell', 'created_at')
    list_filter = ('is_active', 'is_bestsell', 'category')
    search_fields = ('name',)
    
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'image_preview')
    search_fields = ('alt_text',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image Preview'

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__name',)

# -----------------------------
# CART MODELS
# -----------------------------

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal_display',)

    def subtotal_display(self, obj):
        return f"₹{obj.subtotal():.2f}"
    subtotal_display.short_description = 'Subtotal'

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'user_email', 'created_at')
    inlines = [CartItemInline]
    search_fields = ('user__email', 'user__name')
    list_filter = ('created_at',)

    def user_name(self, obj):
        return obj.user.name if obj.user else '-'
    user_name.short_description = 'User Name'
    user_name.admin_order_field = 'user__name'

    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_user_name', 'product', 'quantity', 'subtotal_display')
    list_filter = ('cart__created_at', 'product')
    search_fields = ('product__name', 'cart__user__name')

    def subtotal_display(self, obj):
        return f"₹{obj.subtotal():.2f}"
    subtotal_display.short_description = 'Subtotal'

    def cart_user_name(self, obj):
        return obj.cart.user.name if obj.cart.user else '-'
    cart_user_name.short_description = 'User Name'
    cart_user_name.admin_order_field = 'cart__user__name'

admin.site.register(Cart, CartAdmin)
# admin.site.register(CartItem, CartItemAdmin)

# -----------------------------
# ORDER MODELS
# -----------------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal_display')

    def subtotal_display(self, obj):
        if obj.price is None or obj.quantity is None:
            return "-"
        return f"₹{obj.price * obj.quantity}"
    subtotal_display.short_description = "Subtotal"

def mark_as_delivered(modeladmin, request, queryset):
    updated = queryset.update(status='delivered')
    modeladmin.message_user(request, f"{updated} order(s) marked as delivered.")

mark_as_delivered.short_description = "Mark selected orders as Delivered"

@admin.action(description='Mark selected orders as Paid')
def mark_as_paid(modeladmin, request, queryset):
    updated = queryset.update(is_paid=True)
    modeladmin.message_user(
        request,
        f"{updated} order(s) marked as Paid.",
        messages.SUCCESS
    )

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'full_name', 'phone', 'status', 'is_paid', 'expected_delivery', 'created_at')
    list_filter = ('status', 'is_paid', 'created_at')
    search_fields = ('order_code', 'full_name', 'phone')
    list_editable = ('status',)
    actions = [mark_as_delivered, mark_as_paid]
    inlines = [OrderItemInline]
    readonly_fields = ('payment_screenshot_preview',)

    def payment_screenshot_preview(self, obj):
        if obj.payment_screenshot:
            return format_html('<img src="{}" width="300" />', obj.payment_screenshot.url)
        return "No screenshot uploaded"
    payment_screenshot_preview.short_description = "Payment Screenshot"


    def order_code(self, obj):
        return obj.order_code
    order_code.short_description = 'Order Code'

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Customer Name'

# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('order_code', 'full_name', 'phone', 'status', 'expected_delivery', 'created_at')
#     list_filter = ('status', 'created_at')
#     search_fields = ('order_code', 'full_name', 'phone')
#     list_editable = ('status',)
#     actions = [mark_as_delivered]
#     inlines = [OrderItemInline]

#     # # Razorpay fields are shown as read-only (to view transaction data)
#     # readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')

#     def order_code(self, obj):
#         return obj.order_code
#     order_code.short_description = 'Order Code'

#     def full_name(self, obj):
#         return obj.full_name
#     full_name.short_description = 'Customer Name'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('get_order_code', 'get_order_name', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('order__created_at', 'product')
    search_fields = ('order__order_code', 'order__full_name', 'product__name')

    def get_order_code(self, obj):
        return obj.order.order_code
    get_order_code.short_description = 'Order Code'

    def get_order_name(self, obj):
        return obj.order.full_name
    get_order_name.short_description = 'Customer Name'

    def subtotal(self, obj):
        if obj.price is None or obj.quantity is None:
            return "-"
        return f"₹{obj.price * obj.quantity}"
    subtotal.short_description = "Subtotal"
    
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
# -----------------------------
# WISHLIST MODELS
# -----------------------------
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__email', 'product__name')

admin.site.register(Wishlist, WishlistAdmin)

#reviews
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'comment')

    def user_name(self, obj):
        return obj.user.name or obj.user.email  # Fallback to email if name is blank
    user_name.short_description = 'User'

admin.site.register(Review, ReviewAdmin)

#SOCIAL GIF
@admin.register(SocialOffer)
class SocialOfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_active')
    list_filter = ('is_active',)