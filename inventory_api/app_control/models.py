from django.db import models
from user_control.models import CustomUser
from user_control.views import add_user_activity
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        action = f"Created Inventory Group: {self.name}"
        if self.pk is not None:
            action = f"Updated Inventory Group from '{self.old_name}' to '{self.name}'"
        super().save(*args, **kwargs)

        add_user_activity(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"Deleted Inventory Group: {self.name}"
        super().delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    created_by = models.ForeignKey(CustomUser, null=True, related_name="inventory_items",on_delete=models.SET_NULL)
    code = models.CharField(max_length=100, unique=True, null=True)
    photo = models.TextField(blank=True, null=True)
    groups = models.ForeignKey(InventoryGroup, related_name="inventories", null=True, on_delete=models.SET_NULL)
    total = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=256)
    price = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", )
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            self.remaining = self.total
        
        super().save(*args, **kwargs)

        if is_new:
            id_length = len(str(self.id))
            code_length = 6 - id_length
            zeros = "".join(["0" for i in range(code_length)])
            self.code = f"INV{zeros}{self.id}"
            self.save()
        
        action = f"Created Inventory: {self.name} with code {self.code}"
        if not is_new:
            action = f"Updated Inventory: {self.name} with code {self.code}"
        
        add_user_activity(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"Deleted Inventory: {self.name} with code {self.code}"
        super().delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return f"{self.name} - {self.code}"