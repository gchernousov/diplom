from rest_framework import serializers
from api_backend.models import UserModel, Shop


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'middle_name', 'company', 'position', 'type')


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'owner', 'state')
