from rest_framework import serializers
from api_backend.models import UserModel, ClientContact, Shop, Category, \
    Product, ProductParameter


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'middle_name',
                  'company', 'position', 'type',)


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientContact
        fields = ('id', 'user', 'city', 'street', 'house', 'building', 'apartment', 'phone',)


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'owner', 'state',)


class ShopProductsSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('external_id', 'name', 'category', 'quantity',)


class ShopDetailSerializer(serializers.ModelSerializer):

    products = ShopProductsSerializer(read_only=True, many=True)

    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'owner', 'state', 'products', )


class ProductNameSerializer(serializers.ModelSerializer):

    shop = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'shop', 'price_rcc',)


class CategorySerializer(serializers.ModelSerializer):

    products = ProductNameSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'products',)


class ProductSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField()
    shop = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'shop', 'external_id', 'quantity', 'price', 'price_rcc',)


class ProductParameterSerializer(serializers.ModelSerializer):

    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductDetailSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField()
    shop = serializers.StringRelatedField()
    product_parameters = ProductParameterSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'product_parameters',
                  'shop', 'external_id', 'quantity', 'price', 'price_rcc',)
