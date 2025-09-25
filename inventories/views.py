from rest_framework import viewsets
from .models import Product, Warehouse, Shelve, Inventory, InventoryMovement
from .serializers import InventorySerializer, ProductSerializer, WarehouseSerializer, ShelveSerializer, InventoryMovementSerializer
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError


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
    
    def _delta(self, movement_type: str, qty: int) -> int:
        return qty if movement_type == 'entrada' else -qty  # EntradaProducto => +qty, SalidaProducto => -qty

    @transaction.atomic
    def perform_create(self, serializer):
        movement = serializer.save()
        inv = Inventory.objects.select_for_update().get(pk=movement.inventory.id_inventory)

        delta = self._delta(movement.movement_type, movement.quantity)
        # Validación para no dejar inventario negativo
        if inv.quantity + delta < 0:
            raise ValidationError({"quantity": "Inventario insuficiente para registrar la salida."})

        Inventory.objects.filter(pk=inv.pk).update(quantity=F('quantity') + delta)

    @transaction.atomic
    def perform_update(self, serializer):
        # 1) revertir el efecto anterior del movimiento
        instance = self.get_object()
        inv = Inventory.objects.select_for_update().get(pk=instance.inventory.id_inventory)

        prev_delta = self._delta(instance.movement_type, instance.quantity)
        Inventory.objects.filter(pk=inv.pk).update(quantity=F('quantity') - prev_delta)

        # 2) guardar cambios y aplicar el nuevo efecto
        movement = serializer.save()  # ya puede tener nuevos tipo/cantidad/inventario
        # si cambió de inventario, bloquear el nuevo
        new_inv = Inventory.objects.select_for_update().get(pk=movement.inventory.id_inventory)
        new_inv.refresh_from_db()  # cantidad después de revertir

        new_delta = self._delta(movement.movement_type, movement.quantity)
        if new_inv.quantity + new_delta < 0:
            # deshacer la reversión para no dejar inconsistencia
            Inventory.objects.filter(pk=new_inv.pk).update(quantity=F('quantity') + prev_delta)
            raise ValidationError({"quantity": "Inventario insuficiente para registrar la salida."})

        Inventory.objects.filter(pk=new_inv.pk).update(quantity=F('quantity') + new_delta)

    @transaction.atomic
    def perform_destroy(self, instance):
        inv = Inventory.objects.select_for_update().get(pk=instance.inventory.id_inventory)
        delta = self._delta(instance.movement_type, instance.quantity)

        # al borrar, se revierte el efecto del movimiento
        if inv.quantity - delta < 0:
            raise ValidationError({"quantity": "Eliminar este movimiento dejaría el inventario en negativo."})

        Inventory.objects.filter(pk=inv.pk).update(quantity=F('quantity') - delta)
        instance.delete()
