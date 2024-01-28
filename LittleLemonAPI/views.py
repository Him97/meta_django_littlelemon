from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .forms import BookingForm
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import Group, User
from .models import Category, Booking, Menu, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer,
    UserSerializer
)


def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'book.html', context)


def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, "menu.html", {"menu": main_data})


def display_menu_item(request, pk=None):
    if pk:
        menu_item = Menu.objects.get(pk=pk)
    else:
        menu_item = ""
    return render(request, 'menu_item.html', {"menu_item": menu_item})


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['category__title']
    ordering_fields = ['price', 'inventory']

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response("ok")


class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superusers:
            return Order.objects.all()
        elif self.request.user.groups.count() == 0:
            return Order.objects.all().filter(user=self.request.user)
        elif self.request.user.groups.filter(name="Delivery Crew").exists():
            return Order.objects.all().filter(delivery_crew=self.request.user)
        else:  # delivery crew or manager
            return Order.objects.all()

    def create(self, request, *args, **kwargs):
        menuitem_count = Cart.objects.all().filter(user=self.request.user).count()
        if menuitem_count == 0:
            return Response({"message:": "no item in cart"})

        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data['total'] = total
        data['user'] = self.request.user.id
        order_serializer = OrderSerializer(data=data)
        if (order_serializer.is_valid()):
            order = order_serializer.save()
            items = Cart.objects.all().filter(user=self.request.user).all()
            for item in items.values():
                orderitem = OrderItem(
                    order=order,
                    menuitem=item['menuitem'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                orderitem.save()
            Cart.objects.all().filter(user=self.request.user).delete()
            result = order_serializer.data.copy()
            result['total'] = total
            return Response(order_serializer.data)

    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item['price']
        return total


class SingleOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if self.request.user.group.count() == 0:
            return Response('Not Ok')
        else:
            return super().update(request, *args, **kwargs)


class GroupViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        users = User.objects.all().filter(groups__name='Manager')
        items = UserSerializer(users, many=True)
        return Response(items.data)

    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response({"message": "user added to the manager group"})

    def destory(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({"message": "user removed to the manager group"})


class DeliveryCrewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        users = User.objects.all().filter(group__name='Delivery Crew')
        items = UserSerializer(users, many=True)
        return Response(items.data)

    def create(self, request):  # only for super admin and managers
        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response(
                    {"message": "forbidden"},
                    status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name="Delivery Crew")
        dc.user_set.add(user)
        return Response({"message": "user added to the delivery crew group"}, 200)

    def destroy(self, request):  # only for super admin and managers
        if self.request.user.is_superuser == False:
            if self.request.user.groups.filter(name='Manager').exists() == False:
                return Response({"message": "forbidden"},
                                status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name="Delivery Crew")
        dc.user_set.remove(user)
        return Response(
            {"message": "user removed to the delivery crew group"},
            200)
