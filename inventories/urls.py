from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventories.views import ProductViewSet, BodegaViewSet, ShelveViewSet, InventoryViewSet, InventoryMovementViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"bodegas", BodegaViewSet, basename="bodega")
router.register(r"shelves", ShelveViewSet, basename="shelve")
router.register(r"inventories", InventoryViewSet, basename="inventory")
router.register(r"movements", InventoryMovementViewSet, basename="inventorymovement")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),  # /api/products/ endpoints
]
