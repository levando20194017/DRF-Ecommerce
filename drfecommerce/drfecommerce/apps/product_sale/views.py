from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import ProductSaleSerializer, ProductReportSaleSerializer
from drfecommerce.apps.product_sale.models import ProductSale
from drfecommerce.apps.product_sale.models import ProductSale
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, F

class AdminProductSaleViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    #Thống kê các sản phẩm đã bán, thường là áp dụng trong ngày
    @action(detail=False, methods=['get'], url_path="get-all-products-sale")
    def get_all_products_sale(self, request):
        """
        Get list of product sales with pagination and optional date range filtering.
        
        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        - start_date: The start date to filter product sales (format: YYYY-MM-DD).
        - end_date: The end date to filter product sales (format: YYYY-MM-DD).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        store_id = request.GET.get('store_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Start building the query
        product_sales = ProductSale.objects.all()
        if store_id:
            product_sales = product_sales.filter(store_id = store_id)

        # If start_date or end_date is provided, filter product sales by date range
        if start_date:
            start_date = parse_datetime(f"{start_date} 00:00:00")
            product_sales = product_sales.filter(sale_date__gte=start_date)
        
        if end_date:
            end_date = parse_datetime(f"{end_date} 23:59:59")
            product_sales = product_sales.filter(sale_date__lte=end_date)

        paginator = Paginator(product_sales, page_size)

        try:
            paginated_product_sale = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_product_sale = paginator.page(1)
        except EmptyPage:
            paginated_product_sale = paginator.page(paginator.num_pages)

        serializer = ProductSaleSerializer(paginated_product_sale, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "product_sale": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    #Thống kê doanh thu của từng cửa hàng
    @action(detail=False, methods=['get'], url_path="get-total-report")
    def get_total_report(self, request):
        """
        Get total revenue per store and product quantities sold.
        
        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        - start_date: Filter by start date (optional, format: YYYY-MM-DD).
        - end_date: Filter by end date (optional, format: YYYY-MM-DD).
        - store_id: Filter by store (optional).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        store_id = request.GET.get('store_id')

        # Start building the query
        product_sales = ProductSale.objects.all()

        # Filter by store if provided
        if store_id:
            product_sales = product_sales.filter(store_id=store_id)

        # Filter by date range if provided
        if start_date:
            product_sales = product_sales.filter(sale_date__gte=start_date)
        if end_date:
            product_sales = product_sales.filter(sale_date__lte=end_date)

        # Calculate total revenue for each store
        store_revenue = product_sales.values('store__name').annotate(
            total_revenue=Sum(F('sale_price') * F('quantity_sold')),
            total_quantity_sold=Sum('quantity_sold')
        )

        # Get paginated response
        start = (page_index - 1) * page_size
        end = page_index * page_size
        paginated_data = store_revenue[start:end]

        return Response({
            "status": status.HTTP_200_OK,
            "total_items": store_revenue.count(),
            "data": paginated_data,
        })
        
    @action(detail=False, methods=['get'], url_path="get-list-sold-products-filter")
    def list_sold_products_filter(self, request):
        """
        #Thống kê các product đã bán (số lượng)
        Get the list of sold products with their total quantity sold.
        Optionally filter by start_date, end_date, and store_id.
        Pagination is applied to the response.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        - start_date: The start date to filter product sales (format: YYYY-MM-DD).
        - end_date: The end date to filter product sales (format: YYYY-MM-DD).
        - store_id: The ID of a specific store to filter the sales.
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        store_id = request.GET.get('store_id')

        # Start building the query
        product_sales = ProductSale.objects.all()

        # Filter by store if provided
        if store_id:
            product_sales = product_sales.filter(store_id=store_id)

        # Filter by date range if provided
        if start_date and end_date:
            product_sales = product_sales.filter(sale_date__range=[start_date, end_date])
        elif start_date:
            product_sales = product_sales.filter(sale_date__gte=start_date)
        elif end_date:
            product_sales = product_sales.filter(sale_date__lte=end_date)

        # Group by product and calculate the total quantity sold
        product_sales = product_sales.values('product__id', 'product__name').annotate(
            total_quantity_sold=Sum('quantity_sold')
        )

        # Apply pagination
        paginator = Paginator(product_sales, page_size)

        try:
            paginated_product_sale = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_product_sale = paginator.page(1)
        except EmptyPage:
            paginated_product_sale = paginator.page(paginator.num_pages)

        # Serialize the paginated data
        serializer = ProductReportSaleSerializer(paginated_product_sale, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "product_sale": serializer.data
            }
        }, status=status.HTTP_200_OK)

