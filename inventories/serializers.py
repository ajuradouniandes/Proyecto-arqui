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
        
class WarehouseCreationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_warehouse_creation', 'name', 'location', 'creation_date', 'update_date', 'inventories',)
        model = models.WarehouseCreation

class ShelveSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_shelve', 'name', 'capacity', 'warehouse', 'creation_date', 'update_date',)
        model = models.Shelve

class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_inventory', 'id_product', 'id_warehouse', 'id_shelve', 'quantity', 'creation_date', 'update_date',)
        model = models.Inventory

class InventoryMovementSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_movement', 'inventory', 'movement_type', 'quantity', 'movement_date', 'notes',)
        model = models.InventoryMovement

class OrderCreationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_order_creation', 'order_number', 'status','quantity', 'creation_date', 'update_date', 'product_name', 'inventories',)
        model = models.OrderCreation

class AuditLogSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('order', 'user', 'action_type', 'detail', 'created_at',)
        model = models.AuditLog
    