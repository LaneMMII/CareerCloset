﻿from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from access import models
from access.models import Cart, CartItem, ClothingItem, Transaction, Customer, Favorite, FavoriteItem
from django.contrib.auth.models import Permission

@login_required
def index(request):
    return render(request, 'home.html')

def login(request, *args, **kwargs):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('/admin'))
        else:
            messages.error(request,'username or password not correct')
            return redirect(reverse('/error'))
    else:
        form = AuthenticationForm()
    return render(request,'registration/login.html',{'form':form})

@login_required
def women(request, *args, **kwargs):

    category_name = request.GET.get('category', None)
    category = None
    if category_name:
        category = models.Category.objects.filter(category_name=category_name).first()

    women_clothing_items = []
    title = ""
    women_gender = models.Gender.objects.get(gender_name="Female")
    genderless = models.Gender.objects.get(gender_name = "Genderless")
    if category:
        women_clothing_items = models.ClothingItem.objects.filter(gender=women_gender, availability_status="available", category=category).prefetch_related('images')
        women_clothing_items |= models.ClothingItem.objects.filter(gender=genderless, availability_status="available", category=category).prefetch_related('images')
        if not category_name.endswith('s'):
            title = "Womens " + category_name + "s"
        else:
            title = "Womens " + category_name
    
    else:
        women_clothing_items = models.ClothingItem.objects.filter(gender=women_gender, availability_status="available").prefetch_related('images')
        women_clothing_items |= models.ClothingItem.objects.filter(gender=genderless, availability_status="available").prefetch_related('images')
        title = "Womens Clothing"

    context = {
        'title': title,
        'context': women_clothing_items,
    }
    return render(request, 'women.html', context)

@login_required
def men(request, *args, **kwargs):

    category_name = request.GET.get('category', None)
    category = None
    if category_name:
        category = models.Category.objects.filter(category_name=category_name).first()

    men_clothing_items = []
    title = ""
    men_gender = models.Gender.objects.get(gender_name="Male")
    genderless = models.Gender.objects.get(gender_name="Genderless")

    if category:
        men_clothing_items = models.ClothingItem.objects.filter(gender=men_gender, availability_status="available", category=category).prefetch_related('images')
        men_clothing_items |= models.ClothingItem.objects.filter(gender=genderless, availability_status="available", category=category).prefetch_related('images')
        if not category_name.endswith('s'):
            title = "Mens " + category_name + "s"
        else:
            title = "Mens " + category_name

    else:
        men_clothing_items = models.ClothingItem.objects.filter(gender=men_gender, availability_status="available").prefetch_related('images')
        men_clothing_items |= models.ClothingItem.objects.filter(gender=genderless, availability_status="available").prefetch_related('images')
        title = "Mens Clothing"

    context = {
        'title': title,
        'context': men_clothing_items,
    }
    return render(request, 'men.html', context)

@login_required
def clothing_item_detail(request, clothing_id):
    clothing_item = get_object_or_404(ClothingItem, pk=clothing_id)
    images = clothing_item.images.all() 

    context = {
        'clothing_item': clothing_item,
        'images': images,
    }
    return render(request, 'clothing_item_detail.html', context)

"""
@login_required
def add_to_favorites(request, clothing_id):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated
    
    # Get the Customer instance associated with the logged-in user
    customer = get_object_or_404(Customer, user=request.user)
    
    # Get the ClothingItem instance by clothing_id
    clothing_item = get_object_or_404(ClothingItem, clothing_id=clothing_id)
    
    # Add the clothing item to favorites (if not already in favorites)
    favorite, created = Favorite.objects.get_or_create(customer=customer, clothing_item=clothing_item)
    
    # Redirect to favorites page or any other page as needed
    return redirect('favorites')
"""

@login_required
def add_to_favorites(request, clothing_id):
    # Get or create the Customer profile associated with the current user
    clothing_item = get_object_or_404(ClothingItem, pk=clothing_id)

    # Check if the item is already in the user's favorites
    favorite, created = Favorite.objects.get_or_create(user=request.user, clothing_item=clothing_item)

    if not created:
        messages.info(request, "This item is already in your favorites.")
    else:
        messages.success(request, "Item added to your favorites.")

    return redirect("view_favorites")


@login_required
def view_favorites(request):
    favorite_items = Favorite.objects.filter(user=request.user).select_related('clothing_item')

    return render(request, 'favorites/view_favorites.html', {'favorite_items': favorite_items})

@login_required
def remove_from_favorites(request, favorite_item_id):
    clothing_item = get_object_or_404(ClothingItem, clothing_id=favorite_item_id)
    favorite = get_object_or_404(Favorite, user=request.user, clothing_item=clothing_item)
    favorite.delete()
    return redirect("view_favorites")

@login_required
def add_to_cart(request, clothing_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    clothing_item = get_object_or_404(ClothingItem, pk=clothing_id)

    # Check if the item is already in the cart
    if CartItem.objects.filter(cart=cart, clothing_item=clothing_item).exists():
        messages.info(request, "This item is already in your cart.")
    else:
        # Add item to cart if not already present
        CartItem.objects.create(cart=cart, clothing_item=clothing_item)
        messages.success(request, "Item added to cart.")

    return redirect("view_cart")

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/view_cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect("view_cart")

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    all_available = True
    error_text = ""

    for item in cart.items.all():
        if item.clothing_item.availability_status != 'available':
            all_available = False
            error_text += item.clothing_item.name + " is no longer unavailable. "
    if error_text != "":
        error_text += "Please remove these items and try again"

    if all_available == False:
        return render(request, 'cart/view_cart.html', {'cart': cart, 'error': error_text})

    order = models.Order.objects.create(user=request.user)

    for item in cart.items.all():
        item.clothing_item.availability_status = 'on_order'
        Transaction.objects.create(user=request.user, clothing_item=item.clothing_item, order=order)
        item.clothing_item.save()

    cart.items.all().delete()

    return redirect("/my-orders")

@login_required
def customer_orders(request):
    orders = models.Order.objects.filter(user=request.user)
    print(orders)
    orders = orders.order_by('-order_date')
    print(orders)
    return render(request, 'customer_orders.html', {'orders': orders})

@login_required
@permission_required('access.view_order')
def backend_home(request):

    permissions = request.user.get_all_permissions()
    
    access_permission = 'access.view_accessassignment' in permissions
    order_permission = 'access.view_order' in permissions
    inventory_permission = 'access.view_clothingitem' in permissions
    django_admin_permission = request.user.is_superuser

    context = {
        'access_permission': access_permission,
        'order_permission': order_permission,
        'inventory_permission': inventory_permission,
        'django_admin_permission': django_admin_permission,
    }
    return render(request, 'backend-home.html', context)