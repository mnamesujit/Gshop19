from django import views
from django.db.models.query import FlatValuesListIterable
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerProfileForm, CustomerRegistrationForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ProductView(View):
    def get(self, request):
        totalitem = 0
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html', {'topwears': topwears, 'bottomwears': bottomwears, 'mobiles': mobiles, 'laptops': laptops, 'totalitem': totalitem})


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        totalitem = 0
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()

        return render(request, 'app/productdetail.html', {'product': product, 'item_is_already_cart': item_already_in_cart, 'totalitem': totalitem})


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('product_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()

    return redirect('/cart')


@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        totalitem = len(Cart.objects.filter(user=request.user))
        # print(cart)

        amount = 0.0
        shipping_amount = 49.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        # print(cart_product)

        if cart_product:
            for p in cart_product:
                temp_amount = (p.quantity*p.product.discounted_price)
                amount += temp_amount
                total_amount = amount+shipping_amount
                # print(total_amount)
            return render(request, 'app/addtocart.html', {'carts': cart, 'total_amount': total_amount, 'amount': amount, 'totalitem': totalitem})
        else:
            return render(request, 'app/emptycart.html')


def plus_cart(request):

    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 49.0

        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            temp_amount = (p.quantity*p.product.discounted_price)
            amount += temp_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount+shipping_amount

        }
        return JsonResponse(data)


def minus_cart(request):

    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 49.0

        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            temp_amount = (p.quantity*p.product.discounted_price)
            amount += temp_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount+shipping_amount

        }
        return JsonResponse(data)


def remove_cart(request):

    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 49.0

        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            temp_amount = (p.quantity*p.product.discounted_price)
            amount += temp_amount

        data = {
            'amount': amount,
            'total_amount': amount+shipping_amount

        }
        return JsonResponse(data)


def buy_now(request):
    return render(request, 'app/buynow.html')


@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)

    return render(request, 'app/address.html', {'address': add, 'active': 'btn-primary'})


def mobile(request, data=None):
    totalitem = 0
    mobiles = ""
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'REALME' or data == 'APPLE':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'POCO':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__lt=10000)

    elif data == 'above':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__gt=10000)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/mobile.html', {'mobiles': mobiles, 'totalitem': totalitem})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Congutulations !! Registered Successfully')

            form = CustomerRegistrationForm

        return render(request, 'app/customerregistration.html', {'form': form})


@login_required
def checkout(request):
    totalitem = 0
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 49.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user ==
                    request.user]
    if cart_product:
        for p in cart_product:
            temp_amount = (p.quantity*p.product.discounted_price)
            amount += temp_amount
        total_amount = amount+shipping_amount
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/checkout.html', {'address': add, 'total_amount': total_amount, 'cart_items': cart_items, 'totalitem': totalitem})


@login_required
def payment_done(request):
    user = request.user
    customerid = request.GET.get('customerid')
    customer = Customer.objects.get(id=customerid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer,
                    product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")


@login_required
def orders(request):
    orderplaced = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed': orderplaced})


# Profile View

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality,
                           city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(
                request, 'Congratulations!! Your Profile Updated Successfully')

        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})
