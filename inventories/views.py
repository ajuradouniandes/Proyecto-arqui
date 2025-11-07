from django.utils import timezone
from rest_framework import viewsets
from .models import Product, Warehouse, Shelve, Inventory, InventoryMovement, WarehouseCreation, OrderCreation 
from .serializers import InventorySerializer, ProductSerializer, WarehouseSerializer, ShelveSerializer, InventoryMovementSerializer, WarehouseCreationSerializer, OrderCreationSerializer 
from django.db import transaction, DatabaseError
from django.db.utils import OperationalError
from django.db.models import F
from rest_framework.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache
from rest_framework import request


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id_product')
    serializer_class = ProductSerializer

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by('id_warehouse')
    serializer_class = WarehouseSerializer

class WarehouseCreationViewSet(viewsets.ModelViewSet):
    queryset = WarehouseCreation.objects.all().order_by('id_warehouse_creation')
    serializer_class = WarehouseCreationSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        # Crear una sola bodega
        warehouse = serializer.save()

        # Crear muchas bodegas al mismo tiempo
        warehouses_to_create = []

        for _ in range(100):  # Numero de bodegas para crear
            warehouse_to_create = WarehouseCreation(
                name="Bodega{}".format(_), 
                location="Ubicación{}".format(_),
                creation_date=timezone.now(),
                update_date=timezone.now()
            )
            warehouses_to_create.append(warehouse_to_create)

     
        WarehouseCreation.objects.bulk_create(warehouses_to_create)
        return Response({"detail": "Bodegas creadas correctamente."})
    
    @action(detail=False, methods=['post'])
    def create_multiple(self, request):
        
        data = request.data  # Lista de bodegas 
        
        # Validamos y procesamos en un solo bulk create
        warehouses_to_create = []
        for item in data:
            warehouse_to_create = WarehouseCreation(
                name=item['name'],
                location=item['location'],
                creation_date=timezone.now(),
                update_date=timezone.now()
            )
            warehouses_to_create.append(warehouse_to_create)

        WarehouseCreation.objects.bulk_create(warehouses_to_create)
        return Response({"detail": "Bodegas creadas correctamente."})  
        


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


def _no_store(response):
    # Se colocan encabezados para que no se guarde la respuesta que siempre esta disponible en el cache del balanceador
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response

class OrderCreationViewSet(viewsets.ModelViewSet):
    queryset = OrderCreation.objects.all()
    serializer_class = OrderCreationSerializer

    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
            # Validar y crear el pedido usando el serializer
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                

                # Si la red está caída, guarda el pedido en caché (usa order_number como clave temporal)
                cache_key = f'order_{serializer.validated_data.get("order_number")}'
                cache.set(cache_key, {
                    'product_name': serializer.validated_data.get('product_name'),
                    'quantity': serializer.validated_data.get('quantity'),
                    'order_number': serializer.validated_data.get('order_number'),
                    'creation_date': serializer.validated_data.get('creation_date'),
                    'update_date': serializer.validated_data.get('update_date'),
                    'inventories': serializer.validated_data.get('inventories'),
                }, timeout=10)  # Timeout 
        
        
                order = serializer.save()
                cache.delete(cache_key)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=201, headers=headers)
    
        except DatabaseError as e:
            # Si ocurre un error, se elimina el pedido de la caché  
            print('Error al guardar el pedido en la base de datos:', e)
            print('El pedido permanece en caché para reintentar más tarde.')
            pass
        except OperationalError as e:
            print('Error operativo al guardar el pedido en la base de datos:', e)
            print('El pedido permanece en caché para reintentar más tarde.')
            pass
        except Exception as e:
            print('Error inesperado al guardar el pedido en la base de datos:', e)
            print('El pedido permanece en caché para reintentar más tarde.')
            pass
        
        return Response(serializer.data, status=201)

        
    
    def save_order_to_cache(request):
        order_data = request.data
        cache.set(f'order_{order_data["id"]}', order_data, timeout=600)
        return JsonResponse({"message": "Order saved in cache"})
    
    def sync_cached_orders():
        for key in cache.keys('order_*'):
            order_data = cache.get(key)
            if order_data:
                # Guardar el pedido en la base de datos
                OrderCreation.objects.create(**order_data)
                cache.delete(key)  # Elimina la entrada de la caché después de sincronizarla

@require_http_methods(["GET", "HEAD"])
def health_check(request):

    res = JsonResponse({"status": "ok"})
    return _no_store(res)
