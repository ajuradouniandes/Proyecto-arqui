from rest_framework import serializers
from . import models


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_product', 'name', 'description', 'price', 'creation_date', 'update_date',)
        model = models.Product

class WarehouseSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_warehouse', 'name', 'location', 'creation_date', 'update_date',)
        model = models.Warehouse

class ShelveSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_shelve', 'name', 'capacity', 'warehouse', 'creation_date', 'update_date',)
        model = models.Shelve

class InventorySerializer(serializers.ModelSerializer):
    
    id_product   = serializers.IntegerField(source='id_product')
    id_warehouse = serializers.IntegerField(source='id_warehouse')
    id_shelve    = serializers.IntegerField(source='id_shelve')

    class Meta:
        fields = ('id_inventory', 'id_product', 'id_warehouse', 'id_shelve', 'quantity', 'creation_date', 'update_date',)
        model = models.Inventory

class InventoryMovementSerializer(serializers.ModelSerializer):
    
    inventory = serializers.IntegerField(source='id_inventiry')

    class Meta:
        fields = ('id_movement', 'inventory', 'movement_type', 'quantity', 'movement_date', 'notes',)
        model = models.InventoryMovement