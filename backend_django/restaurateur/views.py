import collections

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from geoapp.models import Coordinate
from geoapp.views import get_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    menu_items = RestaurantMenuItem.objects.select_related('restaurant').select_related('product')
    restaurant_items = collections.defaultdict(list)
    restaurant_address = {}
    coordinates = [coordinate for coordinate in Coordinate.objects.all()]

    for item in menu_items:
        if item.availability:
            restaurant_items[item.restaurant.name].append(item.product.name)
        if not restaurant_address.get(item.restaurant.name):
            restaurant_address[item.restaurant.name] = item.restaurant.address

    orders = [{
        'id': order.pk,
        'status': order.get_status_display(),
        'comment': order.comment,
        'client': f'{order.firstname} {order.lastname}',
        'phone': order.phonenumber,
        'address': order.address,
        'order_price': f'{round(order.order_price)} руб.',
        'payment_method': order.get_payment_method_display(),
        'available_restaurants': sorted([
            get_distance(item, restaurant_address[item], order.address, coordinates)
            for item in restaurant_items
            if all(menu_item in restaurant_items[item] for menu_item in
                   [item.product.name for item in order.items.all()])],
            key=lambda x: float(x.split(' - ')[1].split(' ')[0]) if '-' in x else 0),
        'restaurant': order.restaurant.name if order.restaurant else 'Ресторан не выбран'

    } for order in Order.objects.all().get_order_price()]

    return render(request, template_name='order_items.html', context={
        'orders': orders,
        'current_url': request.path,
    })
