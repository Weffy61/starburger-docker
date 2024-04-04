from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import OrderItem, Order


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    products = OrderItemSerializer(
        many=True,
        write_only=True,
        allow_empty=False
    )
    phonenumber = PhoneNumberField(region="RU")

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']

    def create(self, validated_data):
        order_items_fields = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        order_items = [OrderItem(order=order, price=fields['product'].price, **fields)
                       for fields in order_items_fields]
        OrderItem.objects.bulk_create(order_items)

        return order
