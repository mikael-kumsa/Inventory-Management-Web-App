from rest_framework.viewsets import ModelViewSet
from .serializers import (InventoryGroupSerializer, InventorySerializer, InventoryGroup,
                         Inventory, ShopSerializer, Shop, Invoice, InvoiceSerializer, InvoiceItem,
                          InventoryWithSumSerializer, ShopWithAmountSerializer)
from inventory_api.utils import CustomPagination, get_query
from django.db.models import Count, Sum, F
from django.db.models.functions import Coalesce, TruncMonth
from user_control.models import CustomUser
from rest_framework.response import Response
from inventory_api.custom_methods import IsAuthenticatedCustom


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
    queryset = Invoice.objects.select_related('created_by', 'shop').prefetch_related("invoice_items")
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
            search_fields = ("creatd_by__fullname", "shop__name", "created_by__email")
            query = get_query(keyword, search_fields)
            results = results.filter(query)
        
        return results
    
    def create(self, request, *args, **kwargs):
        request.data.update({'created_by_id': request.user.id})
        return super().create(request, *args, **kwargs)

class SummaryView(ModelViewSet):
    http_method_names = ('get',)
    permission_classes = [IsAuthenticatedCustom]
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        total_inventories = InventoryView.queryset.filter(
            remaining_gt=0
        ).count()
        total_group = InventoryGroupView.queryset.count()
        total_shop = ShopView.queryset.count()
        total_user = CustomUser.objects.filter(is_superuser=False).count()

        return Response({
            "total_inventory": total_inventories,
            "total_group": total_group,
            "total_shop": total_shop,
            "total_user": total_user
        })


class SalePerformanceView(ModelViewSet):
    http_method_names = ('get',)
    permission_classes = [IsAuthenticatedCustom]
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        query_data = request.query_params.dict()
        total = query_data.get("total", None)
        query = self.queryset

        if not total:
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)
            if start_date:
                query = query.filter(
                inventory_invoice__created_at__range = [start_date, end_date]
            )
        
        items = query.annotate(
            sum_of_item = Coalesce(Sum('inventory_invoices__quantity'), 0)
        ).order_by('-sum_of_item')[:10]

        response_data = InventoryWithSumSerializer(items, many=True).data
        return Response(response_data)

class SaleByShopView(ModelViewSet):
    http_method_names = ('get',)
    permission_classes = [IsAuthenticatedCustom]
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        query_data = request.query_params.dict()
        total = query_data.get("total", None)
        monthly = query_data.get("monthly", None)
        query = ShopView.queryset

        if not total:
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)
            if start_date:
                query = query.filter(
                sale_shop__created_at__range = [start_date, end_date]
            )

        if monthly:
            shops = query.annotate(month = TruncMonth('created_at')).values('month', 'name').annotate(
                amount_total = sum(F("sale_shop__invoice_items__quantity") * 
                                   F("sale_shop__invoice_items__amount")
                                   )) 
        else:
            shops = query.annotate(
                amount_total = sum(F("sale_shop__invoice_items__quantity") * 
                                   F("sale_shop__invoice_items__amount")
                                   )).order_by('-amount_total')

        response_data = ShopWithAmountSerializer(shops, many=True).data
        return Response(response_data)
