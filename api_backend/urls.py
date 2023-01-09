from django.urls import path, include
# from api_backend.views import AccountRegister, AccountLogin
from api_backend import views as v


urlpatterns = [
    path('user/register/', v.AccountRegister.as_view()),
    path('user/login/', v.AccountLogin.as_view()),
    path('check/', v.check)
]