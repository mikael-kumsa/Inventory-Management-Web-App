from django.db import models
from user_control.models import CustomUser

# Create your models here.

class InventoryGroup(models.Model):
    created_by = models.ForeignKey(CustomUser, 
                related_name="inventory_group", null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, unique=True)
    belongs_to = models.ForeignKey("self", related_name="group_relations", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", )

    def save(self, *args, **kwargs):
        action = f"Created Inventory Group: {self.name}"