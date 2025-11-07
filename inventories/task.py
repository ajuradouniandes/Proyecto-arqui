from celery import shared_task
from django.core.cache import cache
from .models import Order

@shared_task
def sync_cached_orders():
    for key in cache.keys('order_*'):
        order_data = cache.get(key)
        print('Pedido guardado en cache para guardar en base de datos:', order_data)
        if order_data:
            Order.objects.create(**order_data) 
            cache.delete(key)  # Elimina la entrada de la caché después de sincronizarla
