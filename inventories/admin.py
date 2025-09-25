from django.contrib import admin
from . models import Inventory, Product, Bodega, Shelve

admin.site.register(Inventory)
admin.site.register(Product)
admin.site.register(Bodega)
admin.site.register(Shelve)
