from rest_framework import viewsets
from .models import Product, WhareHouse, Shelve, Inventory, InventoryMovement
from .serializers import InventorySerializer, ProductSerializer, WarehouseSerializer, ShelveSerializer, InventoryMovementSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id_product')
    serializer_class = ProductSerializer

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by('id_warehouse')
    serializer_class = WarehouseSerializer

class ShelveViewSet(viewsets.ModelViewSet):
    queryset = Shelve.objects.all().order_by('id_shelve')
    serializer_class = ShelveSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by('id_inventory')
    serializer_class = InventorySerializer

class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.all().order_by('id_movement')
    serializer_class = InventoryMovementSerializer