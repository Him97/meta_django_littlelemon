from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('menu/', views.menu, name="menu"),
    path('book/', views.book, name="book"),
    path('categories/', views.CategoriesView.as_view()),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('cart/menu-items/', views.CartView.as_view()),
    path('orders/', views.OrderView.as_view()),
    path('orders/<int:pk>/', views.SingleOrderView().as_view()),
    path('groups/manager/users/', views.GroupViewSet.as_view(
        {'get': 'list', 'post': 'create', 'delete': 'destroy'}
    )),
    path('groups/delivery-crew/users/', views.DeliveryCrewViewSet.as_view(
        {'get': 'list', 'post': 'create', 'delete': 'destroy'}
    )),
    path('api-token-auth/', obtain_auth_token)
]
