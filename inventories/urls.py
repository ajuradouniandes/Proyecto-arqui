from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventories.views import ProductViewSet, WarehouseViewSet, ShelveViewSet, InventoryViewSet, InventoryMovementViewSet, health_check


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"warehouses", WarehouseViewSet, basename="warehouse")
router.register(r"shelves", ShelveViewSet, basename="shelve")
router.register(r"inventories", InventoryViewSet, basename="inventory")
router.register(r"movements", InventoryMovementViewSet, basename="inventorymovement")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),  # /api/products/ endpoints
    path("health-check/", include(health_check.urls)),  # /health-check/ endpoints
]
