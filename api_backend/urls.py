from django.urls import path
from api_backend import views as v


urlpatterns = [
    path('user/register/', v.AccountRegister.as_view()),
    path('user/login/', v.AccountLogin.as_view()),
    path('user/contact/', v.ContactView.as_view()),
    path('shop/', v.ShopView.as_view()),
    path('shop/<int:shop_id>', v.ShopDetailView.as_view()),
    path('shop/update/', v.ShopUpdate.as_view()),
    path('shop/orders/', v.ShopOrders.as_view()),
    path('categories/', v.CategoryView.as_view()),
    path('products/', v.ProductView.as_view()),
    path('products/<int:product_id>', v.ProductDetailView.as_view()),
    path('basket/', v.BasketView.as_view()),
    path('order/', v.OrderView.as_view())
]

# Добавить возможность просмотра товаров конкретного магазина
