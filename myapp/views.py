from django.shortcuts import render, redirect
from .models import Category, Product, Offer, Cart, CartItem, Order, OrderItem, Wishlist, Review, SocialOffer # import your Category model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import ReviewForm
from django.contrib import messages
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from accounts.models import CustomUser
from urllib.parse import quote
import threading



#BASE VIEW
def base(request):
    categories = Category.objects.all()

    bestselling = Product.objects.filter(is_bestsell=True, is_active=True)
    row1 = [prod for i, prod in enumerate(bestselling) if i % 2 == 0]
    row2 = [prod for i, prod in enumerate(bestselling) if i % 2 == 1]

    offers = Offer.objects.filter(is_active=True)

    reviews = Review.objects.select_related('user').order_by('-created_at')

    social_offers = SocialOffer.objects.filter(is_active=True)

    cart_product_ids = []
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_product_ids = list(cart.items.values_list('product_id', flat=True))

    context = {
        'categories': categories,
        'row1': row1,
        'row2': row2,
        'offers': offers,
        'reviews': reviews,
        'social_offers': social_offers,
        'cart_product_ids': cart_product_ids,
    }

    return render(request, 'pages/home.html', context)

def about(request):
    return render(request, 'pages/aboutUs.html')


def check_auth_view(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})


#PRODUCT VIEWS
def categories(request):
    categories = Category.objects.all()
    return render(request, 'pages/product_categories.html', {'categories': categories})

def products(request, name):
    category = get_object_or_404(Category, name=name)
    categories = Category.objects.all()
    products = Product.objects.filter(category=category)

    cart_product_ids = []
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_product_ids = list(cart.items.values_list('product_id', flat=True))

    return render(request, 'pages/products.html', {
        'products': products,
        'selected_category': category,
        'category_name': name,
        'categories': categories,
        'cart_product_ids': cart_product_ids,
    })

def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    in_wishlist = False
    in_cart = False

    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            in_cart = cart.items.filter(product=product).exists()

    return render(request, 'pages/product_details.html', {
        'product': product,
        'in_wishlist': in_wishlist,
        'in_cart': in_cart,
    })

#CART VIEWS
def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key or request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
    item.save()
    return redirect('view_cart')


def view_cart(request):
    user = request.user
    # Get the cart for this user; create if it doesn't exist
    cart, created = Cart.objects.get_or_create(user=user)

    total = 0
    for item in cart.items.all():
        total += item.subtotal()

    context = {
        'cart': cart,
        'total': total,
    }
    return render(request, 'pages/mycart.html', context)

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('view_cart')

def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.quantity = int(request.POST.get('quantity', 1))
    item.save()
    return redirect('view_cart')

#CHECKOUT VIEWS

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    total = sum(item.subtotal() for item in cart.items.all())
    # total_paise = int(total * 100)  # Razorpay expects amount in paise

    user = request.user
    
    # Define UPI ID (could be in settings or DB)
    upi_id = '9003689821@okbizaxis'  # replace with your UPI or fetch dynamically
    

    # Build UPI link with amount and payee name (URL-encoded)
    upi_link = (
    f"upi://pay?"
    f"pa={upi_id}"
    f"&am={total}"
    f"&cu=INR"
    )
    # Create Razorpay payment
    # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    # payment = client.order.create({
    #     "amount": total_paise,
    #     "currency": "INR",
    #     "payment_capture": "1"
    # })

    # Final context with everything
    context = {
        'cart': cart,
        'total': total,
        # 'razorpay_order_id': payment['id'],
        # 'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        # 'currency': 'INR',
        # 'amount': total_paise,
        'total': total,
        'upi_id': upi_id,
        'upi_link': upi_link,
        'user_data': {
            'name': user.name,
            'phone': user.mobile,
            'pincode': user.pincode,
            'city': user.city,
            'address': user.address
        }
    }

    return render(request, 'pages/checkout.html', context)

@login_required
@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)

        # Save address info
        user = request.user
        user.pincode = request.POST.get('pincode')
        user.city = request.POST.get('city')
        user.address = request.POST.get('address')
        user.save()

        screenshot = request.FILES.get('payment_screenshot')

        # Create order
        order = Order.objects.create(
            user=user,
            full_name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            payment_method='Static UPI Screenshot',
            payment_screenshot=screenshot,
            is_paid=False
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Email message
        subject = f'Order #{order.order_code} — Payment Screenshot Uploaded'
        message = f"Customer: {order.full_name}\nPhone: {order.phone}\nCity: {order.city}\nPincode: {order.pincode}\nAddress: {order.address}\nState: {order.state}\n\n"
        message += "Order placed with manual payment. Screenshot uploaded.\n\n"
        message += "Ordered Items:\n"
        for item in order.items.all():
            message += f"- {item.product.name} (Qty: {item.quantity}) - ₹{item.price * item.quantity}\n"
        message += f"\nTotal: ₹{sum(i.price * i.quantity for i in order.items.all())}"

        # Background email sending function
        def send_order_emails():
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, ['indiaculture24@gmail.com'])
                send_mail(f"Order Received #{order.order_code}",
                          f"Thank you for your payment! We will verify it shortly and confirm your order.\n\n{message}",
                          settings.EMAIL_HOST_USER, [user.email])
            except Exception as e:
                print(f"Email send failed: {e}")

        threading.Thread(target=send_order_emails).start()

        # Clear cart
        cart.items.all().delete()

        return render(request, 'pages/order_confirmation.html', {'order': order})
    
# @login_required
# @csrf_exempt 
# def place_order(request):
#     if request.method == 'POST':
#         cart = get_object_or_404(Cart, user=request.user)

#         # Razorpay payment details
#         razorpay_payment_id = request.POST.get("razorpay_payment_id")
#         razorpay_order_id = request.POST.get("razorpay_order_id")
#         razorpay_signature = request.POST.get("razorpay_signature")
        
#         user = request.user
#         user.pincode = request.POST.get('pincode')
#         user.city = request.POST.get('city')
#         user.address = request.POST.get('address')

#         user.save()
        

#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         try:
#             client.utility.verify_payment_signature({
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature
#             })
#         except:
#             return render(request, 'pages/payment_failed.html')

#         # If payment is successful
#         order = Order.objects.create(
#             user=request.user,
#             full_name=request.POST.get('name'),
#             phone=request.POST.get('phone'),
#             address=request.POST.get('address'),
#             city=request.POST.get('city'),
#             state=request.POST.get('state'),
#             pincode=request.POST.get('pincode'),
#             payment_method='UPI (Razorpay)',
#             razorpay_order_id=razorpay_order_id,
#             razorpay_payment_id=razorpay_payment_id,
#             razorpay_signature=razorpay_signature,
#         )

#         for item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 price=item.product.price,
#             )

#         # Send Email
#         subject = f'New Order #{order.order_code}'
#         message = f"Customer: {order.full_name}\nPhone: {order.phone}\nCity: {order.city}\n\n"
#         message += "Ordered Items:\n"
#         for item in order.items.all():
#             message += f"- {item.product.name} (Qty: {item.quantity}) - ₹{item.price * item.quantity}\n"
#         message += f"\nTotal: ₹{sum(i.price * i.quantity for i in order.items.all())}"
        
#         # To Owner
#         send_mail(subject, message, settings.EMAIL_HOST_USER, ['connect.procols@gmail.com'])

#         # To Customer
#         send_mail(f"Order Confirmation #{order.order_code}", f"Thank you for your order!\n\n{message}", settings.EMAIL_HOST_USER, [request.user.email])

#         # Clear Cart
#         cart.items.all().delete()

#         return render(request, 'pages/order_confirmation.html', {'order': order})

    
# MY ORDER VIEWS
@login_required
def myorder(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    for order in orders:
        order.total_price = sum(item.price * item.quantity for item in order.items.all())
    
    return render(request, 'pages/myorder.html', {'orders': orders})



# WATCHLIST VIEWS
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'pages/wishlist.html', {'wishlist_items': wishlist_items})

# reviews
@login_required
def submit_review(request):
    if Review.objects.filter(user=request.user).exists():
        messages.info(request, "You have already submitted a review.")
        return redirect('home')  # This will show the message on the homepage

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('home')
    else:
        form = ReviewForm()

    return render(request, 'pages/submit_review.html', {'form': form})

# custon error page
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    return render(request, '403.html', status=403)