from django.contrib import admin
from .models import Inventory, InventoryGroup


admin.site.register((Inventory, InventoryGroup))

