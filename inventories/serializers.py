from rest_framework import serializers
from . import models


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_product', 'name', 'description', 'price', 'creation_date', 'update_date',)
        model = models.Product

class BodegaSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_bodega', 'name', 'location', 'creation_date', 'update_date',)
        model = models.Bodega

class ShelveSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_shelve', 'name', 'capacity', 'bodega', 'creation_date', 'update_date',)
        model = models.Shelve

class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id_inventory', 'id_product', 'id_bodega', 'id_shelve', 'quantity', 'creation_date', 'update_date',)
        model = models.Inventory