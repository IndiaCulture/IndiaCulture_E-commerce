from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='home'),
    path('about/', views.about, name='about'),

    path('check-auth/', views.check_auth_view, name='check_auth'),

    path('categories/', views.categories, name='categories'),
    path('products/<str:name>/', views.products, name='products'),
    path('product_details/<int:product_id>/', views.product_details, name='product_details'),

    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),

    path('myorder/', views.myorder, name='myorder'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('submit-review/', views.submit_review, name='submit_review')
]
