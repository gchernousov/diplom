from rest_framework import serializers
from api_backend.models import UserModel


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'middle_name', 'company', 'position', 'type')
