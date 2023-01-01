from rest_framework.viewsets import ModelViewSet
from .serializers import InventoryGroupSerializer, InventorySerializer, InventoryGroup, Inventory, ShopSerializer, Shop, Invoice, InvoiceSerializer
from inventory_api.custom_methods import IsAuthenticatedCustom
from inventory_api.utils import CustomPagination, get_query
from django.db.models import Count

class InventoryView(ModelViewSet):
    queryset = Inventory.objects.select_related('group', 'created_by')
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.queryset.method != "GET":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)

        results = get_query(**data)

        if keyword:
            search_fields = ("code", "creatd_by__fullname", "group__name", "name", "created_by__email")
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        return results

    def create(self, request, *args, **kwargs):
        request.data.update({'created_by_id': request.user.id})
        return super().create(request, *args, **kwargs)

class InventoryGroupView(ModelViewSet):
    queryset = InventoryGroup.objects.select_related('belongs_to', 'created_by').prefetch_related('inventories')
    serializer_class = InventoryGroupSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.queryset.method.lower() != "GET":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)

        results = get_query(**data)

        if keyword:
            search_fields = ("creatd_by__fullname", "name", "created_by__email")
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        return results.annotate(
            total_items=Count('inventories')
        )
    
    def create(self, request, *args, **kwargs):
        request.data.update({'created_by_id': request.user.id})
        return super().create(request, *args, **kwargs)

class ShopView(ModelViewSet):
    queryset = Shop.objects.select_related('created_by')
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.queryset.method.lower() != "GET":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)

        results = get_query(**data)

        if keyword:
            search_fields = ("creatd_by__fullname", "name", "created_by__email")
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results
    
    def create(self, request, *args, **kwargs):
        request.data.update({'created_by_id': request.user.id})
        return super().create(request, *args, **kwargs)

class InvoiceView(ModelViewSet):
    queryset = Invoice.objects.select_related('created_by', 'shop')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticatedCustom]
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.queryset.method.lower() != "GET":
            return self.queryset
        
        data = self.request.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)

        results = get_query(**data)

        if keyword:
            search_fields = ("creatd_by__fullname", "name", "created_by__email")
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results
    
    def create(self, request, *args, **kwargs):
        request.data.update({'created_by_id': request.user.id})
        return super().create(request, *args, **kwargs)