from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import ProductSaleSerializer, ProductReportSaleSerializer
from drfecommerce.apps.product_sale.models import ProductSale
from drfecommerce.apps.product_store.models import ProductStore
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.product.serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action, permission_classes, authentication_classes
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime
from drfecommerce.apps.product_incoming.models import ProductIncoming
from drfecommerce.apps.order.models import Order
from django.db.models import DecimalField
from datetime import timedelta

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
        
    @action(detail=False, methods=['get'], url_path="get-sales-and-incomings")
    def get_sales_and_incomings(self, request):
        # Lấy các tham số đầu vào từ query params
        # Thống kê tổng số lượng, giá tiền đã nhập và đã bán theo từng ngày
        store_id = request.query_params.get('store_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date and not end_date:
            print(start_date, end_date)
            try:
                latest_sale_date = ProductSale.objects.filter(store_id=store_id).latest('sale_date').sale_date
                latest_incoming_date = ProductIncoming.objects.filter(store_id=store_id).latest('effective_date').effective_date
                
                print(latest_sale_date, latest_incoming_date)
                # Ngày gần nhất giữa cả hai bảng
                latest_date = max(latest_sale_date, latest_incoming_date).date()
                end_date = latest_date
                start_date = end_date - timedelta(days=30)  # Lấy 1 tháng trước đó
                print(start_date, end_date)
            except ProductSale.DoesNotExist and ProductIncoming.DoesNotExist:
                return Response({"error": "No data available for this store."}, status=404)
            
        # print(start_date, end_date)
        # Nếu ngày được cung cấp, chuyển đổi chúng sang datetime.date
        try:
            # Chuyển đổi start_date và end_date chỉ khi chúng là chuỗi
            if start_date and isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

            if end_date and isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Lọc dữ liệu bán hàng
        sales_data = ProductSale.objects.filter(
            store_id=store_id,
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date
        ).values('sale_date__date').annotate(
            total_revenue=Sum(F('sale_price') * F('quantity_sold'), output_field=DecimalField()),
            total_quantity=Sum('quantity_sold')
        ).order_by('sale_date__date')

        
        # Lọc dữ liệu nhập kho
        incoming_data = ProductIncoming.objects.filter(
            store_id=store_id,
            effective_date__date__gte=start_date,
            effective_date__date__lte=end_date
        ).values('effective_date__date').annotate(
            total_cost=Sum(F('cost_price') * F('quantity_in'), output_field=DecimalField()),
            total_quantity=Sum('quantity_in')
        ).order_by('effective_date__date')


        # Chuẩn bị dữ liệu trả về
        chart_data = {
            "labels": [],  # Labels cho các ngày
            "series": [
                {
                    "name": "Sales Revenue",
                    "data": []
                },
                {
                    "name": "Sales Quantity",
                    "data": []
                },
                {
                    "name": "Incoming Cost",
                    "data": []
                },
                {
                    "name": "Incoming Quantity",
                    "data": []
                }
            ]
        }

        # Tập hợp các ngày có trong cả sales_data và incoming_data
        all_dates = set(sale['sale_date__date'] for sale in sales_data) | set(incoming['effective_date__date'] for incoming in incoming_data)
        all_dates = sorted(all_dates)

        # Tạo từ điển dữ liệu
        sales_dict = {sale['sale_date__date']: sale for sale in sales_data}
        incoming_dict = {incoming['effective_date__date']: incoming for incoming in incoming_data}

        chart_data = {
            "labels": [],  # Labels cho các ngày
            "series": [
                {"name": "Sales Revenue", "data": []},
                {"name": "Sales Quantity", "data": []},
                {"name": "Incoming Cost", "data": []},
                {"name": "Incoming Quantity", "data": []},
            ]
        }

        # Duyệt qua các ngày để xây dựng dữ liệu
        for date in all_dates:
            chart_data["labels"].append(date.strftime('%Y-%m-%d'))
            
            # Bán hàng
            if date in sales_dict:
                chart_data["series"][0]["data"].append(float(sales_dict[date]['total_revenue']))
                chart_data["series"][1]["data"].append(sales_dict[date]['total_quantity'])
            else:
                chart_data["series"][0]["data"].append(0)
                chart_data["series"][1]["data"].append(0)
            
            # Nhập kho
            if date in incoming_dict:
                chart_data["series"][2]["data"].append(float(incoming_dict[date]['total_cost']))
                chart_data["series"][3]["data"].append(incoming_dict[date]['total_quantity'])
            else:
                chart_data["series"][2]["data"].append(0)
                chart_data["series"][3]["data"].append(0)
                
        return Response({
          "data": chart_data,
          "status": 200   
        }, status=200)

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
            productStore = ProductStore.objects.filter(store=store_id).order_by('-updated_at')
            # Áp dụng phân trang cho sản phẩm
            
            
            product_data = []
            for product_store in productStore:
                product = product_store.product
                product_data.append(product)
            
            paginator = Paginator(product_data, page_size)
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



