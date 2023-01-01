from .models import Inventory, InventoryGroup, Shop, Invoice, InvoiceItem
from rest_framework import serializers
from user_control.serializers import CustomUserSerializer

class InventoryGroupSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    created_by = serializers.CharField(write_only=True)
    belongs_to = serializers.SerializerMethodField(read_only=True)
    belongs_to_id = serializers.CharField(write_only=True)
    total_items = serializers.CharField(read_only=True, required=False)



    class Meta:
        model = InventoryGroup
        fields = '__all__'

    def get_belongs_to(self, obj):
        if obj.belongs_to is not None:
            return InventoryGroupSerializer(obj.belongs_to).data
        return None


class Inventory(serializers.ModelSerializer):
    created_by = serializers.CharField(write_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    group = InventoryGroupSerializer(read_only=True)
    group_id = serializers.CharField(write_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'

class ShopSerializer(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    amount_total = serializers.CharField(read_only=True, required=False)
    count_total = serializers.CharField(read_only=True, required=False)
    
    class Meta:
        model = Shop
        fields = '__all__'

class InvoiceItemSerializer(serializers.ModelSerializer):
    invoice = serializers.CharField(read_only=True)
    invoice_id = serializers.CharField(write_only=True)
    item = serializers.CharField(read_only=True)
    item_id = serializers.CharField(write_only=True)

    class Meta:
        model = InvoiceItem
        fields = '__all__'
    

class InvoiceItemDataSerializer(serializers.ModelSerializer):
        item_id = serializers.CharField()
        quantity = serializers.IntegerField()

class InvoiceSerializer(serializers.ModelSerializer):
    created_by = CustomUserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False)
    shop = ShopSerializer(read_only=True)
    shop_id = serializers.CharField(write_only=True)
    invoice_items = InvoiceItemSerializer(many=True, read_only=True)
    invoice_item_data = InvoiceItemDataSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Invoice
        fields = '__all__'

    def create(self, validated_data):
        invoice_item_data = validated_data.pop('invoice_item_data')

        if not invoice_item_data:
            raise Exception("You Need to add at least one item to the invoice")

        invoice = super().create(validated_data)

        invoice_item_serializer = InvoiceItemSerializer(data=[{"invoice_id": invoice.id, **item} for item in invoice_item_data], many=True)

        if invoice_item_serializer.is_valid():
            invoice_item_serializer.save()
        else:
            invoice.delete()
            raise Exception(invoice_item_serializer.errors)

        return invoice