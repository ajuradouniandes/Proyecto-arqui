from django.contrib import admin
from . models import Inventory, Product, Warehouse, Shelve, WarehouseCreation, OrderCreation

admin.site.register(Inventory)
admin.site.register(Product)
admin.site.register(Warehouse)
admin.site.register(Shelve)
admin.site.register(WarehouseCreation)
admin.site.register(OrderCreation)