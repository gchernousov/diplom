from django.urls import path, include
# from api_backend.views import AccountRegister, AccountLogin
from api_backend import views as v


urlpatterns = [
    path('user/register/', v.AccountRegister.as_view()),
    path('user/login/', v.AccountLogin.as_view()),
    path('shop/', v.ShopView.as_view()),
    path('shop/<int:shop_id>', v.ShopDetailView.as_view()),
    path('shop/update/', v.ShopUpdate.as_view()),
    path('categories/', v.CategoryView.as_view()),
    path('products/', v.ProductView.as_view()),
    path('check/', v.check)
]
