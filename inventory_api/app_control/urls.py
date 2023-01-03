from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (InventoryView, InventoryGroupView, ShopView, SummaryView, PurchaseView, 
SaleByShopView, SalePerformanceView, InvoiceView, InventoryCSVLoaderView)

router = DefaultRouter(trailing_slash=False)

router.register(r'inventory', InventoryView, 'inventory')
router.register(r'inventory-csv', InventoryCSVLoaderView, 'inventory-csv')
router.register(r'shop', ShopView, 'shop')
router.register(r'summary', SummaryView, 'summary')
router.register(r'purchase-summary', PurchaseView, 'purchase-summary')
router.register(r'sale-by-shop', SaleByShopView, 'sales-by-shop')
router.register(r'group', InventoryGroupView, 'group')
router.register(r'top-selling', SalePerformanceView, 'top-selling')
router.register(r'invoice', InvoiceView, 'invoice')

urlpatterns = [
    path('', include(router.urls)),
]
