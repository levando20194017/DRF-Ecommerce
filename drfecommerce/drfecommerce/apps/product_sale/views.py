from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import ProductSaleSerializer, ProductReportSaleSerializer
from drfecommerce.apps.product_sale.models import ProductSale
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.product.serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action, permission_classes, authentication_classes
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
        product_sales = ProductSale.objects.all().order_by('-updated_at')
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
        product_sales = ProductSale.objects.all().order_by('-updated_at')

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

@authentication_classes([])            
@permission_classes([AllowAny])      
class PublicProductSaleViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path="get-list-sold-products-filter")
    def list_sold_products_filter(self, request):
        """
        Thống kê các sản phẩm đã bán (số lượng)=> sắp xếp theo bán chạy nhất.
        Nếu không có sản phẩm bán nào, trả về danh sách sản phẩm mặc định từ bảng Product.
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        store_id = request.GET.get('store_id')

        # Lấy danh sách sản phẩm đã bán
        product_sales = ProductSale.objects.all().order_by('-updated_at')

        # Lọc theo cửa hàng (nếu có)
        if store_id:
            product_sales = product_sales.filter(store_id=store_id)

        # Lọc theo ngày (nếu có)
        if start_date and end_date:
            product_sales = product_sales.filter(sale_date__range=[start_date, end_date])
        elif start_date:
            product_sales = product_sales.filter(sale_date__gte=start_date)
        elif end_date:
            product_sales = product_sales.filter(sale_date__lte=end_date)

        # Gộp theo sản phẩm và tính tổng số lượng đã bán
        product_sales = product_sales.values('product__id', 'product__name').annotate(
            total_quantity_sold=Sum('quantity_sold')
        ).order_by('-total_quantity_sold')  # Sắp xếp theo số lượng bán được nhiều nhất

        # Nếu danh sách sản phẩm đã bán rỗng, lấy danh sách mặc định từ bảng Product
        if len(product_sales) < 4:
            products = Product.objects.all()
            products = products.order_by('-updated_at')
            # Áp dụng phân trang cho sản phẩm
            paginator = Paginator(products, page_size)
            try:
                paginated_products = paginator.page(page_index)
            except PageNotAnInteger:
                paginated_products = paginator.page(1)
            except EmptyPage:
                paginated_products = paginator.page(paginator.num_pages)

            # Serialize danh sách sản phẩm
            serializer = ProductSerializer(paginated_products, many=True)
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Không có sản phẩm nào được bán, trả về danh sách sản phẩm mặc định.",
                "data": {
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "page_index": page_index,
                    "page_size": page_size,
                    "products": serializer.data
                }
            }, status=status.HTTP_200_OK)

        # Áp dụng phân trang cho danh sách sản phẩm đã bán
        product_ids = [item['product__id'] for item in product_sales]
        products = Product.objects.filter(id__in=product_ids).order_by('-updated_at')

        # Áp dụng phân trang
        paginator = Paginator(products, page_size)
        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        # Serialize danh sách sản phẩm
        serializer = ProductSerializer(paginated_products, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Thành công",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "products": serializer.data
            }
        }, status=status.HTTP_200_OK)

