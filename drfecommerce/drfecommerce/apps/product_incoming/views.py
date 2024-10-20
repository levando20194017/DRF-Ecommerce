from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.product_store.models import ProductStore
from .models import ProductIncoming
from .serializers import ProductIncomingSerializer,ProductIncomingDetailSerializer
from drfecommerce.apps.product_store.serializers import ProductStoreSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.utils.dateparse import parse_datetime
from django.db.models import Sum

class ProductIncomingViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path="create-product-incoming")
    def add_product_incoming(self, request):
        """
        Add ProductIncoming and update ProductStore stock.
        Request body:
        - product_id
        - store_id
        - cost_price
        - quantity_in
        - vat
        - shipping_cost
        - effective_date (optional) YYYY-MM-DD HH:MM:SS
        """
        product_id = request.data.get('product_id')
        store_id = request.data.get('store_id')
        cost_price = request.data.get('cost_price')
        quantity_in = int(request.data.get('quantity_in', 0))
        vat = request.data.get('vat', 0)
        shipping_cost = request.data.get('shipping_cost', 0)
        effective_date = request.data.get('effective_date', timezone.now())
        # Validate product and store existence
        try:
            product = Product.objects.get(id=product_id)
            store = Store.objects.get(id=store_id)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Store.DoesNotExist:
            return Response({"message": "Store not found."}, status=status.HTTP_404_NOT_FOUND)

        # Create a new ProductIncoming entry
        product_incoming = ProductIncoming.objects.create(
            product=product,
            store=store,
            cost_price=cost_price,
            quantity_in=quantity_in,
            vat=vat,
            shipping_cost=shipping_cost,
            effective_date=effective_date
        )
        
        # Update or create ProductStore entry
        product_store, created = ProductStore.objects.get_or_create(product=product, store=store)
        product_store.quantity_in += quantity_in  # Add the incoming quantity to existing stock
        product_store.remaining_stock += quantity_in  # Update remaining stock
        product_store.save()

        return Response({
            "message": "ProductIncoming added and ProductStore updated successfully.",
            "product_incoming": ProductIncomingSerializer(product_incoming).data,
            "product_store": ProductStoreSerializer(product_store).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path="delete-product-incoming")
    def delete_product_incoming(self, request):
        """
        Hard delete ProductIncoming and update ProductStore stock.
        Query params:
        - id (ProductIncoming ID)
        """
        product_incoming_id = request.query_params.get('id')

        if not product_incoming_id:
            return Response({"message": "ProductIncoming ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the ProductIncoming entry
            product_incoming = ProductIncoming.objects.get(id=product_incoming_id)
        except ProductIncoming.DoesNotExist:
            return Response({"message": "ProductIncoming not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update ProductStore before deletion
        try:
            product_store = ProductStore.objects.get(product=product_incoming.product, store=product_incoming.store)
            product_store.quantity_in -= product_incoming.quantity_in  # Decrease the quantity_in
            product_store.remaining_stock -= product_incoming.quantity_in  # Decrease the remaining stock
            product_store.save()
        except ProductStore.DoesNotExist:
            return Response({"message": "ProductStore not found."}, status=status.HTTP_404_NOT_FOUND)

        # Finally, delete ProductIncoming entry
        product_incoming.delete()

        return Response({
            "message": "ProductIncoming deleted and ProductStore updated successfully."
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path='list-product-incomings')
    def list_product_incomings(self, request):
        """
        API lấy danh sách các sản phẩm nhập vào theo khoảng thời gian và store với phân trang.
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - store_id: ID của store để lọc (có thể truyền hoặc không)
        - start_date: ngày bắt đầu để lọc (YYYY-MM-DD) (có thể truyền hoặc không)
        - end_date: ngày kết thúc để lọc (YYYY-MM-DD) (có thể truyền hoặc không)
        """
        # Nhận page_index và page_size từ query params
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        # Nhận các tham số lọc
        store_id = request.GET.get('store_id', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        # Tạo queryset ban đầu
        product_incomings = ProductIncoming.objects.all()

        # Lọc theo store nếu có truyền store_id
        if store_id:
            product_incomings = product_incomings.filter(store_id=store_id)

        # Lọc theo ngày (start_date và end_date) nếu có truyền
        if start_date:
            start_date = parse_datetime(f"{start_date}T00:00:00")
            product_incomings = product_incomings.filter(effective_date__gte=start_date)
        if end_date:
            end_date = parse_datetime(f"{end_date}T23:59:59")
            product_incomings = product_incomings.filter(effective_date__lte=end_date)

        # Sử dụng Paginator để phân trang
        paginator = Paginator(product_incomings, page_size)

        try:
            paginated_product_incomings = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_product_incomings = paginator.page(1)
        except EmptyPage:
            paginated_product_incomings = paginator.page(paginator.num_pages)

        # Serialize dữ liệu
        serializer = ProductIncomingSerializer(paginated_product_incomings, many=True)

        # Trả về response có phân trang và dữ liệu lọc
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "product_incomings": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['get'], url_path='detail-product-incoming')
    def detail_product_incoming(self, request):
        """
        API lấy chi tiết một sản phẩm nhập vào theo ID
        """
        product_incoming_id = request.query_params.get('id')
        if not product_incoming_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Product incoming ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            product_incoming = ProductIncoming.objects.get(id=product_incoming_id)
        except ProductIncoming.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "ProductIncoming not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductIncomingDetailSerializer(product_incoming)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path='search-product-incoming')
    def search_product_incomings(self, request):
        """
        API tìm kiếm sản phẩm nhập vào theo tên sản phẩm, store và khoảng thời gian.
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - store_id: ID của store để lọc (có thể truyền hoặc không)
        - start_date: ngày bắt đầu để lọc (YYYY-MM-DD)
        - end_date: ngày kết thúc để lọc (YYYY-MM-DD)
        - product_name: tên sản phẩm để tìm kiếm
        """
        # Nhận page_index và page_size từ query params
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        # Nhận các tham số lọc
        store_id = request.GET.get('store_id', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name', None)

        # Tạo queryset ban đầu
        product_incomings = ProductIncoming.objects.all()

        # Lọc theo store nếu có truyền store_id
        if store_id:
            product_incomings = product_incomings.filter(store_id=store_id)

        # Lọc theo ngày (start_date và end_date) nếu có truyền
        if start_date:
            start_date = parse_datetime(f"{start_date}T00:00:00")
            product_incomings = product_incomings.filter(effective_date__gte=start_date)
        if end_date:
            end_date = parse_datetime(f"{end_date}T23:59:59")
            product_incomings = product_incomings.filter(effective_date__lte=end_date)

        # Lọc theo tên sản phẩm nếu có truyền product_name
        if product_name:
            product_incomings = product_incomings.filter(product__name__icontains=product_name)

        # Sử dụng Paginator để phân trang
        paginator = Paginator(product_incomings, page_size)

        try:
            paginated_product_incomings = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_product_incomings = paginator.page(1)
        except EmptyPage:
            paginated_product_incomings = paginator.page(paginator.num_pages)

        # Serialize dữ liệu
        serializer = ProductIncomingSerializer(paginated_product_incomings, many=True)

        # Trả về response có phân trang và dữ liệu lọc
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "product_incomings": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="expenditure-statistics")
    def expenditure_statistics(self, request):
        #Tính tổng tiền chi để mua sản phẩm
        """
        Get total expenditure with VAT and shipping costs.
        
        Optional Parameters:
        - store_id: ID of the store to filter by.
        - start_date: Start date for filtering expenditures (optional).
        - end_date: End date for filtering expenditures (optional).
        """
        store_id = request.GET.get('store_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        filter_kwargs = {}
        if store_id:
            filter_kwargs['store_id'] = store_id
        if start_date:
            filter_kwargs['effective_date__gte'] = start_date
        if end_date:
            filter_kwargs['effective_date__lte'] = end_date

        expenditures = ProductIncoming.objects.filter(**filter_kwargs).aggregate(
            total_cost=Sum('cost_price') + Sum('vat') + Sum('shipping_cost')
        )

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Expenditure statistics retrieved successfully.",
            "data": {
                "total_expenditure": expenditures.get('total_cost', 0)
            }
        }, status=status.HTTP_200_OK)