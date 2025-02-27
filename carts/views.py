from decimal import Decimal
from django.shortcuts import render , redirect , get_object_or_404
from products.models import Product , Variation , Coupon
from .models import Cart , CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import CouponApplyForm
from django.utils import timezone
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try :
                    variation = Variation.objects.get(product=product,variation_category__iexact=key , variation_value__iexact=value)
                    product_variation.append(variation)
                    # print(product_variation)
                except:
                    pass
        
        is_cart_item_exists = CartItem.objects.filter(product=product , user=current_user).exists()
        if is_cart_item_exists :
            cart_item = CartItem.objects.filter(product=product , user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item = CartItem.objects.get(product=product , id=item_id)
                item.quantity+=1
                item.save()
                messages.success(request,"Product added successfully")
            else :
                item = CartItem.objects.create(product=product , quantity = request.POST["quantity"], user=current_user)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                messages.success(request,"Product added successfully")
        else :
            cart_item = CartItem.objects.create(
                product=product,
                quantity = request.POST["quantity"] , 
                user = current_user ,
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            messages.success(request,"Product added successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try :
                    variation = Variation.objects.get(product=product,variation_category__iexact=key , variation_value__iexact=value)
                    product_variation.append(variation)
                    # print(product_variation)
                except:
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product , cart=cart).exists()
        if is_cart_item_exists :
            cart_item = CartItem.objects.filter(product=product , cart = cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item = CartItem.objects.get(product=product , id=item_id)
                item.quantity+=int(request.POST["quantity"])
                item.save()
                messages.success(request,"Product added successfully")
            else :
                item = CartItem.objects.create(product=product , quantity = request.POST["quantity"], cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                messages.success(request,"Product added successfully")
        else :
            cart_item = CartItem.objects.create(
                product=product,
                quantity = request.POST["quantity"] , 
                cart = cart ,
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            messages.success(request,"Product added successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def decrement_cart(request , product_id,cart_item_id):
    
    product = get_object_or_404(Product , id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product , user = request.user , id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product , cart = cart , id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request,"Product removed successfully")
        else:
            cart_item.delete()
            messages.success(request,"Product deleted successfully")
    except:
        pass
    return redirect('cart')

def delete_cart(request , product_id ,cart_item_id):
    
    product = get_object_or_404(Product , id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product , user = request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product , cart = cart,id=cart_item_id)
    cart_item.delete()
    messages.success(request,"Product deleted successfully")
    return redirect('cart')

def cart(request , total = 0 , quantity = 0 , cart_items = None):
    
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user , is_active = True)            

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart , is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
        
    except ObjectDoesNotExist:
        pass
    context = {
        'total':total ,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request , 'cart.html' , context)

@login_required(login_url='login')
def checkout(request, total = 0 , quantity = 0 , cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user , is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart , is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total':total ,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request , 'checkout.html',context)

def apply_coupon(request):
    now = timezone.now()
    if request.method == 'POST':
        code = request.POST.get('coupon')
        try:
            coupon = Coupon.objects.get(
                code__iexact = code,
                valid_from__lte = now,
                valid_to__gte = now,
                is_expired = False
            )
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('cart')